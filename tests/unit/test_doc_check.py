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
from collections.abc import Mapping, Sequence
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

#: The test the default `MODEL` fixture's bound family names. `_repo` defines
#: it in a suite of its own, so a fixture repository resolves its own citation
#: and `check_named_tests` has nothing to decline.
FAMILY_TEST = "test_the_demo_says_it_is_a_demo"
#: The list-shaped family's test, deliberately a second name: `_family_model`
#: rewrites every occurrence of `FAMILY_TEST`, so a fixture sharing one name
#: between the two families would rewrite both and make each hazard-table
#: test assert about a second error it never meant to raise.
LIST_FAMILY_TEST = "test_the_demo_shows_the_time_it_is_at"

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
        # A conforming bound family, for the same reason as the marker above:
        # `check_bound_families` errors on a family whose heading it cannot
        # find, so a fixture without one would fail every test that asserts a
        # clean repository stays clean. Last, so that the provenance table
        # stays the one thing "## Known limitations" follows.
        "## Reasonably foreseeable misuse, and the hazards the presentation carries",
        "",
        "| A reader could be misled into | What stops it | Held by |",
        "| --- | --- | --- |",
        f"| reading a demo value as a real one | it says so | `{FAMILY_TEST}` |",
        "",
        # The second shape, for the same reason: `BOUND_FAMILIES` holds a
        # list-shaped family too, and it errors on a heading it cannot find,
        # so a fixture without one would fail every test asserting that a
        # clean repository stays clean. The second entry wraps, because that
        # is the shape `_list_members` has to fold and the real section is
        # full of it.
        "## Minimum displayed outputs",
        "",
        "The interface must show:",
        "",
        f"- the demo value (`{LIST_FAMILY_TEST}`);",
        "- the time the demo value was read at",
        f"  (`{LIST_FAMILY_TEST}`).",
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
    tests: bool = True,
) -> Path:
    """Build a miniature repository with the structure the checker reads.

    `tests=False` builds one with no suite at all, which is the shape a bare or
    truncated checkout has and the only thing `check_named_tests` declines on.
    """
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
    if tests:
        suite = root / "tests" / "unit"
        suite.mkdir(parents=True, exist_ok=True)
        (suite / "test_family.py").write_text(
            f"def {FAMILY_TEST}() -> None:\n    pass\n\n\n"
            f"def {LIST_FAMILY_TEST}() -> None:\n    pass\n",
            encoding="utf-8",
        )
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


def test_a_citation_the_process_cannot_stat_is_reported_not_raised(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """One unstattable token must not take every other citation with it.

    Found 2026-09-19 and live again on 2026-09-21: a documentation line cited
    the container's agent-proxy README by absolute path, under a directory
    mode 700 for the unprivileged user CI runs as. `_resolves` raised
    `PermissionError` out of `Path.exists` and `doc_check` reported nothing at
    all about any of the ~1,279 citations around it, while `make check` stayed
    green in the session that wrote the line (`PL-D1NT`; `PL-0M7L` is the same
    failure in the `glob` branch above, guarded since).

    The raise is driven rather than staged, because this suite's interpreter
    can no longer produce one. Through 3.13 `Path.exists` re-raises any
    `OSError` outside ENOENT, ENOTDIR, EBADF and ELOOP; 3.14 rewrote it to
    `return os.path.exists(self)`, which swallows all of them - so the defect
    is live under the `python3 tools/doc_check.py check` that CI and a bare
    checkout run, and invisible under the pinned 3.14 that runs these tests.
    Patching the method this resolver must not use is what pins the fix on the
    interpreters where it matters: restore `Path.exists` here and this fails,
    on any version.
    """
    token = "refused/only-here.md"
    unpatched = Path.exists

    def refusing_exists(self: Path, *, follow_symlinks: bool = True) -> bool:
        if str(self).endswith(token):
            raise PermissionError(13, "Permission denied")
        return unpatched(self, follow_symlinks=follow_symlinks)

    monkeypatch.setattr(Path, "exists", refusing_exists)

    readme = f"# Demo\n\nSee `{token}` and `core/moved.py`.\n"

    errors = _errors(_repo(tmp_path, readme=readme))

    assert any(f"cites `{token}`" in e for e in errors)
    # The regression is the second line, not the first: an unguarded stat
    # aborted `analyze` before any later citation was judged at all.
    assert any("cites `core/moved.py`" in e for e in errors)


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


def test_a_quoted_measurement_before_above_is_not_a_citation(tmp_path: Path) -> None:
    """Prose contrasting a figure with the one it replaced is not a citation.

    Observed 2026-09-05 writing a measurement into `docs/WORKING_NOTES.md`:
    the sentence quoted the old figure as it appeared in the note, and the run
    hard-failed with `cites section "~88-256 B each" in this file`. The only
    repair available was to reword prose that was not wrong, which teaches a
    session to avoid quotation marks in documentation (`PL-KJ63`).
    """
    readme = '# Demo\n\nEach entry now costs 12 B, against "~88-256 B each" above.\n'

    assert not any("cites section" in e for e in _errors(_repo(tmp_path, readme=readme)))


def test_a_directed_citation_opening_on_a_letter_still_resolves(tmp_path: Path) -> None:
    """The narrowing must not swallow the form it exists to check."""
    readme = '# Demo\n\nSee "Renamed limitations" above for what it omits.\n'

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


def test_a_section_mark_citation_is_checked_like_a_comma_one(tmp_path: Path) -> None:
    """The form this project actually writes, and the one it went unchecked in.

    `QUOTED_SOURCE_RE` allowed only `,` or `:` between the document and the
    quotation, so every `§` citation matched nothing — and matching nothing is
    silent. Measured 2026-09-13: 285 of the tree's 324 document-section
    citations were in the `§` form, against 39 in the comma form, while the run
    reported that the citations in the documentation, the queue and the source
    docstrings all resolved (`PL-V13T`).
    """
    root = _repo(tmp_path)
    _item(root, "PL-0000-demo", '**Context.** `docs/MODEL.md` § "A thread that was deleted".\n')
    assert any(
        'PL-0000-demo.md:1: quotes docs/MODEL.md as "A thread that was deleted"' in e
        for e in _errors(root)
    )


def test_a_section_mark_citation_that_resolves_is_not_an_error(tmp_path: Path) -> None:
    root = _repo(tmp_path)
    _item(root, "PL-0000-demo", '**Context.** `docs/MODEL.md` § "Known limitations".\n')
    assert not any("quotes docs/MODEL.md" in e for e in _errors(root))


def test_an_under_citation_after_the_document_is_checked(tmp_path: Path) -> None:
    """`` `doc.md` under "X" `` - 11 in the tree, and `under` says outright it cites."""
    root = _repo(tmp_path)
    _item(root, "PL-0000-demo", '**Context.** `docs/MODEL.md` under "A deleted thread".\n')
    assert any("quotes docs/MODEL.md" in e for e in _errors(root))


def test_a_parenthesised_citation_is_checked(tmp_path: Path) -> None:
    root = _repo(tmp_path)
    _item(root, "PL-0000-demo", '**Context.** `docs/MODEL.md` ("A deleted thread").\n')
    assert any("quotes docs/MODEL.md" in e for e in _errors(root))


def test_a_possessive_quotation_of_absent_text_is_reported(tmp_path: Path) -> None:
    """The possessive is read like every other connective, and for one reason.

    `` `CLAUDE.md`'s "..." `` quotes a *sentence* as often as it cites a
    section, and `PL-V13T` excluded it because nothing distinguishes the two
    without reading the meaning. The distinction was never needed: this check
    tests containment, so it asks one question of both uses - whether the
    cited file holds the words - and a quotation that has drifted is as stale
    as a title that has. Re-measured 2026-09-21, a majority of what the
    exclusion suppressed was real drift (`PL-316G`).
    """
    root = _repo(tmp_path)
    _item(root, "PL-0000-demo", '**Context.** `docs/MODEL.md`\'s "a sentence not in it".\n')
    assert any("quotes docs/MODEL.md" in e for e in _errors(root))


def test_a_possessive_quotation_of_text_that_is_there_passes(tmp_path: Path) -> None:
    """Admitting the form is not the same as failing every use of it.

    The constraint the widening adds is that a quotation in quotation marks
    has to be quotable; prose quoted faithfully is still correct prose, and
    holding that here is what keeps the check from reading as a ban on the
    possessive (`PL-316G`).
    """
    root = _repo(tmp_path)
    _item(root, "PL-0000-demo", '**Context.** `docs/MODEL.md`\'s "Known limitations".\n')
    assert not any("quotes docs/MODEL.md" in e for e in _errors(root))


def test_a_citation_wrapping_inside_a_blockquote_is_not_reported_stale(tmp_path: Path) -> None:
    """A `>` opening the continued line belongs to the blockquote, not the quote.

    Eleven citations of one heading that is present were reported stale this
    way, all of them the Qt-port deferral note the project owner added to six
    item files (`PL-V13T`).
    """
    root = _repo(tmp_path)
    _item(
        root, "PL-0000-demo", '> **Deferred.** `docs/MODEL.md` § "Known\n> limitations" names it.\n'
    )
    assert not any("quotes docs/MODEL.md" in e for e in _errors(root))


def test_citation_in_a_source_docstring_is_held_to_the_document_it_names(tmp_path: Path) -> None:
    """A contributor reading the class is sent somewhere; it has to still answer."""
    root = _repo(tmp_path)
    _docstringed(root, 'See `docs/MODEL.md`, "A thread that was deleted".')
    assert any("thing.py:1: quotes docs/MODEL.md" in e for e in _errors(root))


@pytest.mark.parametrize(
    ("source", "declined"),
    [
        (b'"""See `docs/MODEL.md`, "A thread that was deleted"."""\n\ndef f(:\n', ":3: Python "),
        (b'"""See `docs/MODEL.md`, "A deleted caf\xe9"."""\n', ":1: Python "),
    ],
    ids=["unparseable", "undecodable"],
)
def test_a_source_file_the_running_interpreter_cannot_parse_is_reported_not_skipped(
    tmp_path: Path, source: bytes, declined: str
) -> None:
    """A source file this run cannot read is named as unread, never passed over.

    The source is written for 3.14, and CI's floor section also runs this
    under 3.11, whose parser stops at a PEP 695 generic. Such a file was
    skipped with nothing said, and `make check`, then bare too, printed "all
    resolve" over docstrings it had never read (`PL-MB3F`). Both sources here
    fail to parse under every interpreter, so the test holds wherever it runs.
    """
    root = _repo(tmp_path)
    (root / "src" / "anesthesia_sim" / "core" / "thing.py").write_bytes(source)
    report = doc_check.analyze(root)
    about = [line for line in report.declined if "thing.py" in line]
    assert len(about) == 1 and f"core/thing.py{declined}" in about[0], report.declined
    assert not any("thing.py" in error for error in report.errors)
    assert "all resolve" not in doc_check.format_check(report)


def test_a_source_file_with_a_byte_order_mark_is_read_not_declined(tmp_path: Path) -> None:
    """Python reads source as bytes and honours the mark, so this has to as well.

    Decoding the text first leaves U+FEFF in front of the module, which the
    parser rejects, and the file would be declined with advice to run a newer
    interpreter that would not help.
    """
    root = _repo(tmp_path)
    (root / "src" / "anesthesia_sim" / "core" / "thing.py").write_bytes(
        b'\xef\xbb\xbf"""See `docs/MODEL.md`, "A thread that was deleted"."""\n'
    )
    report = doc_check.analyze(root)
    assert not any("thing.py" in line for line in report.declined), report.declined
    assert any("thing.py:1: quotes docs/MODEL.md" in error for error in report.errors)


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


def test_a_closed_brief_quoting_a_deleted_heading_is_not_an_error(tmp_path: Path) -> None:
    """A closed brief says what was true when the work was done, not what is.

    `check_line_citations` has always drawn this line and `check_quoted_sources`
    did not, so the two checks disagreed about the same file. The disagreement
    was not academic: `ROADMAP.md`'s `## Current baseline` section is replaced
    wholesale at every release, so a closed brief quoting one of its headings
    went red at the next cut, and the only ways out were repairing a historical
    record or editing the roadmap to suit a check (`PL-ZM8P`).
    """
    root = _repo(tmp_path)
    _item(root, "PL-0000-done", _brief("done", '`docs/MODEL.md`, "A thread that was deleted".'))

    assert not any("quotes docs/MODEL.md" in e for e in _errors(root))


def test_an_open_brief_quoting_a_deleted_heading_is_still_an_error(tmp_path: Path) -> None:
    """The live half is untouched, which is what makes the exemption narrow.

    Without this, skipping closed briefs would be indistinguishable from
    switching the check off.
    """
    root = _repo(tmp_path)
    _item(root, "PL-0000-open", _brief("ready", '`docs/MODEL.md`, "A thread that was deleted".'))

    assert any("quotes docs/MODEL.md" in e for e in _errors(root))


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


# --- citations of a path .gitignore covers ----------------------------------


def _ignoring(root: Path, rules: str) -> Path:
    """`root` as a real checkout whose `.gitignore` holds `rules`.

    Real git run from `PATH`, like `_git_init` below and for the same reason:
    what is under test is how the checker reads git's answer, so a stub would
    test the stub. No commit is made - `git check-ignore --no-index` reads the
    rules alone, which is also what makes the exemption answerable in a bare
    checkout.
    """
    (root / ".gitignore").write_text(rules, encoding="utf-8")
    subprocess.run(("git", "init", "-q"), cwd=root, check=True, capture_output=True)
    return root


def test_a_cited_path_gitignore_covers_is_not_required_to_exist(tmp_path: Path) -> None:
    """`docs/worker.md` names `out/` precisely because nothing tracks it.

    The repository has a category the checker could not express before
    `PL-MXSL`: a path that is *meant* to be absent, named in documentation on
    purpose. Writing it without its trailing slash was the only way to comply,
    which is a rule no reader of either file could discover.
    """
    readme = "# Demo\n\nGenerated files go in `out/`.\n"
    root = _ignoring(_repo(tmp_path, readme=readme), "/out/\n")

    assert not any("cites `out/`" in e for e in _errors(root))


def test_the_verdict_is_the_same_whether_the_ignored_directory_is_there_or_not(
    tmp_path: Path,
) -> None:
    """The defect was a verdict that depended on the working tree.

    `make check` passed wherever a session had just rendered a screenshot into
    `out/` and CI failed on identical content - one tree giving two answers,
    rather than a missing feature. A path git will never carry is one the
    working tree can only answer wrongly about in one of the two places.
    """
    readme = "# Demo\n\nGenerated files go in `out/`.\n"
    root = _ignoring(_repo(tmp_path, readme=readme), "/out/\n")

    absent = _errors(root)
    (root / "out").mkdir()
    (root / "out" / "dashboard.png").write_text("", encoding="utf-8")

    assert _errors(root) == absent


def test_a_path_that_is_neither_ignored_nor_present_still_errors(tmp_path: Path) -> None:
    """The exemption is the whole of the hole it opens, and no wider."""
    readme = "# Demo\n\nGenerated files go in `nosuch/`.\n"
    root = _ignoring(_repo(tmp_path, readme=readme), "/out/\n")

    assert any("cites `nosuch/`" in e for e in _errors(root))


def test_a_file_an_ignore_rule_re_admits_is_not_exempt(tmp_path: Path) -> None:
    """Why git answers this question and a reader of `.gitignore` does not.

    `.vscode/*` excludes the directory's contents and `!.vscode/settings.json`
    re-admits the tracked project settings, so that file is *not* covered and a
    citation of it must still resolve. Parsing the anchored directory rules
    alone - the narrower form the item weighed - would call it exempt and stop
    checking a tracked file.
    """
    readme = "# Demo\n\nEditor settings live in `.vscode/settings.json`.\n"
    root = _ignoring(_repo(tmp_path, readme=readme), ".vscode/*\n!.vscode/settings.json\n")

    assert any("cites `.vscode/settings.json`" in e for e in _errors(root))


def test_a_braced_citation_is_exempt_only_when_every_expansion_is_covered(tmp_path: Path) -> None:
    """Half an exemption is none: `_resolves` takes any expansion, this takes all."""
    readme = "# Demo\n\nOutput goes to `{out,build}/report.txt` and `{out,dist}/log.txt`.\n"
    root = _ignoring(_repo(tmp_path, readme=readme), "/out/\n/dist/\n")

    errors = _errors(root)

    assert any("cites `{out,build}/report.txt`" in e for e in errors)
    assert not any("cites `{out,dist}/log.txt`" in e for e in errors)


def test_a_token_outside_the_repository_is_reported_rather_than_exempted(tmp_path: Path) -> None:
    """Fails closed - and this is the token shape that rules out the batch form.

    `git check-ignore` exits 128 on a path outside the repository, and
    `--stdin` aborts the whole run on the first one: measured over this store's
    own citations it died on `fatal: //: '//' is outside repository` after 49
    answers of 1,549. Per token it costs one citation's exemption and nothing
    else.
    """
    readme = "# Demo\n\nSee `../elsewhere/`.\n"
    root = _ignoring(_repo(tmp_path, readme=readme), "/out/\n")

    assert any("cites `../elsewhere/`" in e for e in _errors(root))


def test_no_git_on_path_reports_the_citation_rather_than_exempting_it(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Every way git can decline is read as *not* covered.

    The exemption is granted only on a positive answer, so a checkout that
    cannot run git is held to exactly the rule it was held to before.
    """
    readme = "# Demo\n\nGenerated files go in `out/`.\n"
    root = _ignoring(_repo(tmp_path, readme=readme), "/out/\n")
    assert not any("cites `out/`" in e for e in _errors(root))

    monkeypatch.setenv("PATH", "")

    assert any("cites `out/`" in e for e in _errors(root))


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


def test_candidate_line_is_labelled_with_the_most_specific_term(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """A line kept once has to be labelled by one of the terms that found it.

    Keeping whichever arrived first labelled it by the sort order: a changed
    `thing.py` contributes both `thing` and `thing.py`, `thing` sorts first,
    and a line plainly about the module printed as `(thing)` (`PL-Z0G0`).
    """
    readme = README + "\nThe `thing.py` module is where that lives.\n"
    root = _repo(tmp_path, readme=readme)
    _git_init(root)

    module = root / "src" / "anesthesia_sim" / "core" / "thing.py"
    module.write_text("def advance_thing() -> None:\n    return None\n", encoding="utf-8")

    assert doc_check.main(["candidates", "--root", str(root), "--base", "HEAD"]) == 0
    labelled = [
        line for line in capsys.readouterr().out.splitlines() if "README.md" in line and "(" in line
    ]

    assert labelled, "the line naming `thing.py` should be a candidate"
    assert any("(thing.py)" in line for line in labelled)
    assert not any(line.endswith("(thing)") for line in labelled)


def test_candidates_mode_is_quiet_when_nothing_changed(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = _repo(tmp_path)
    _git_init(root)
    assert doc_check.main(["candidates", "--root", str(root), "--base", "HEAD"]) == 0
    assert "nothing to sweep" in capsys.readouterr().out


def test_candidates_mode_says_it_could_not_read_the_diff(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """A diff git would not produce is not an empty one (`PL-9RFP`).

    `_git` answered a failure with an empty list, and every caller reads that
    as nothing changed. A base that did not resolve, or a checkout that is not
    a repository at all, printed "nothing to sweep", and the close-out sweep
    was skipped over a diff nobody had read. The test above this one pinned
    that answer for a checkout with no repository in it, until it was given
    one.
    """
    root = _repo(tmp_path)
    assert doc_check.main(["candidates", "--root", str(root), "--base", "HEAD"]) == 1
    outside = capsys.readouterr().out
    assert "Cannot sweep" in outside
    assert "nothing to sweep" not in outside

    _git_init(root)
    assert doc_check.main(["candidates", "--root", str(root), "--base", "no-such-base-ref"]) == 1
    unresolved = capsys.readouterr().out
    assert "no-such-base-ref" in unresolved
    assert "nothing to sweep" not in unresolved


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


def _commit_version_file(root: Path, text: str, subject: str) -> None:
    """Commit `pyproject.toml` holding `text`, even where that changes nothing."""
    (root / "pyproject.toml").write_text(text, encoding="utf-8")
    for command in (("add", "-A"), ("commit", "-qm", subject, "--allow-empty")):
        subprocess.run(("git", *command), cwd=root, check=True, capture_output=True)


def _tagged(
    tmp_path: Path,
    *names: str,
    roadmap: str = VERSIONED_ROADMAP,
    declaring: Mapping[str, str] | None = None,
) -> Path:
    """A versioned repository that is a git checkout holding the tags given.

    Each tag goes on a commit of its own whose `pyproject.toml` declares that
    tag's version, as a release cut leaves it, and the tree then returns to the
    version the roadmap names current. Stacking every tag on one commit was
    enough until a tag's own tree was read, and is now the finding itself
    (`PL-YKSD`). `declaring` gives a tag's commit another version instead.
    """
    root = _versioned(tmp_path, roadmap=roadmap)
    current = (root / "pyproject.toml").read_text(encoding="utf-8")
    _git_init(root)
    for name in names:
        version = (declaring or {}).get(name, name.removeprefix("v"))
        _commit_version_file(
            root, f'[project]\nname = "demo"\nversion = "{version}"\n', f"cut {name}"
        )
        # Real tags, made with real git - see `_git_init` above.
        subprocess.run(("git", "tag", name), cwd=root, check=True, capture_output=True)
    _commit_version_file(root, current, "the current baseline")
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


# PL-YKSD: a tag's name says which release it is for, and only its own tree says
# whether it sits on that release's commit.

STALE_CLAIM = "\n\n**One version shipped with a stale version file**: v0.2.4.\n"


def _short(root: Path, revision: str) -> str:
    shown = subprocess.run(
        ("git", "rev-parse", "--short", revision),
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )
    return shown.stdout.strip()


def test_a_tag_whose_pyproject_version_disagrees_is_refused(tmp_path: Path) -> None:
    """v0.5.3's instance: pushed before its release merged, onto the commit before it.

    Every check read that tag as right because every check read only its name.
    Annotated, as this project's tags are, so the commit the message has to name
    is the one the tag peels to rather than the tag object's own hash.
    """
    root = _tagged(tmp_path, "v0.2.4")
    subprocess.run(
        ("git", "tag", "-a", "v0.2.5", "-m", "v0.2.5", "v0.2.4^{commit}"),
        cwd=root,
        check=True,
        capture_output=True,
    )
    commit = _short(root, "v0.2.5^{commit}")
    assert commit != _short(root, "v0.2.5"), "the fixture must be an annotated tag"

    errors = _errors(root)

    # The same reading is what a clone still holding a tag the remote deleted
    # sees, where moving the tag is the wrong repair (`PL-LT77`).
    assert any(
        f"v0.2.5 points at {commit}" in message
        and "declares 0.2.4" in message
        and "git tag -d v0.2.5" in message
        for message in errors
    ), errors


def _git(root: Path, *args: str) -> str:
    done = subprocess.run(("git", *args), cwd=root, check=True, capture_output=True, text=True)
    return done.stdout.strip()


def _cut(root: Path, name: str) -> str:
    """Cut `name` as a release does, its notes and its version in one commit; its short hash."""
    notes = root / "docs" / "releases" / f"{name}.md"
    notes.parent.mkdir(parents=True, exist_ok=True)
    notes.write_text(f"## {name}\n", encoding="utf-8")
    version = name.removeprefix("v")
    _commit_version_file(root, f'[project]\nname = "demo"\nversion = "{version}"\n', f"cut {name}")
    return _short(root, "HEAD")


def test_a_tag_ahead_of_its_own_cut_is_named(tmp_path: Path) -> None:
    """`PL-KFWL`: one merge past its cut, a tag still declares its version, so only the cut sees it.

    That is the tag `origin/main` put on the next merge when it was tagged late
    (`PL-VYK1`). The message names both commits, and the version check says
    nothing more about a tag already reported.
    """
    root = _tagged(tmp_path, "v0.2.4")
    cut = _cut(root, "v0.2.5")
    _commit_version_file(root, (root / "pyproject.toml").read_text(), "the next merge")
    _git(root, "tag", "-a", "v0.2.5", "-m", "v0.2.5")
    late = _short(root, "v0.2.5^{commit}")

    errors = _errors(root)

    assert any(
        f"v0.2.5 points at `{late} the next merge`, which did not add docs/releases/v0.2.5.md"
        in message
        and f"Its own history says that is `{cut} cut v0.2.5`, so move it there" in message
        and "git tag -d v0.2.5" in message
        for message in errors
    ), errors
    assert not any("declares" in message for message in errors), errors


def test_a_tag_behind_its_own_cut_is_named(tmp_path: Path) -> None:
    """Tagged before its release merged, and on a commit already declaring its version."""
    root = _tagged(tmp_path, "v0.2.4")
    before = _short(root, "HEAD")
    _cut(root, "v0.2.5")
    _git(root, "tag", "-a", "v0.2.5", "-m", "v0.2.5", "HEAD^")

    errors = _errors(root)

    assert any(
        f"v0.2.5 points at `{before} the current baseline`" in message
        and "None in its own history did, so it sits before its release was cut" in message
        for message in errors
    ), errors


def test_a_tag_on_its_cut_is_quiet_on_a_branch_that_merged_it_in(tmp_path: Path) -> None:
    """Read from `HEAD`, this branch's own merge would be taken for the cut (`PL-QHCW`)."""
    root = _tagged(tmp_path, "v0.2.4")
    trunk = _git(root, "rev-parse", "--abbrev-ref", "HEAD")
    _git(root, "checkout", "-qb", "feature")
    (root / "work.txt").write_text("work\n", encoding="utf-8")
    _git(root, "add", "-A")
    _git(root, "commit", "-qm", "feature work")
    _git(root, "checkout", "-q", trunk)
    _cut(root, "v0.2.5")
    _git(root, "tag", "-a", "v0.2.5", "-m", "v0.2.5")
    _git(root, "checkout", "-q", "feature")
    _git(root, "merge", "-q", "--no-edit", trunk)

    assert _errors(root) == []


def test_a_version_named_as_shipping_with_a_stale_version_file_is_excused(tmp_path: Path) -> None:
    """v0.2.0's case: the tag is on the commit that shipped, which never bumped.

    Moving that tag onto the later bump would claim the bump shipped in the
    release it corrected, so the exception is written down instead - and it
    excuses only the version the sentence names.
    """
    roadmap = VERSIONED_ROADMAP.replace("tag.\n", "tag." + STALE_CLAIM, 1)
    root = _tagged(tmp_path, "v0.2.4", "v0.2.5", roadmap=roadmap, declaring={"v0.2.4": "0.2.3"})

    assert _errors(root) == []


def test_a_stale_version_file_claim_the_tag_contradicts_is_an_error(tmp_path: Path) -> None:
    """An exception left standing after its tag is repaired excuses the next mistake."""
    roadmap = VERSIONED_ROADMAP.replace("tag.\n", "tag." + STALE_CLAIM, 1)
    errors = _errors(_tagged(tmp_path, "v0.2.4", "v0.2.5", roadmap=roadmap))

    assert any(
        "v0.2.4 is named as shipping with a stale version file, but" in message
        for message in errors
    ), errors


def test_a_stale_version_file_count_is_held_to_its_names(tmp_path: Path) -> None:
    claim = STALE_CLAIM.replace("One version", "Two versions")
    roadmap = VERSIONED_ROADMAP.replace("tag.\n", "tag." + claim, 1)
    errors = _errors(_versioned(tmp_path, roadmap=roadmap))

    assert any(
        "says Two shipped with a stale version file, but names 1" in message for message in errors
    ), errors


def test_a_tag_whose_tree_yields_no_version_is_declined_rather_than_refused(tmp_path: Path) -> None:
    """A tree with no version to read is a question unanswered, not a wrong answer.

    An empty read cannot say whether the file is absent at that commit or
    merely absent from this clone, so it is reported as not checked rather
    than as a tag on the wrong commit.
    """
    root = _tagged(tmp_path, "v0.2.5")
    current = (root / "pyproject.toml").read_text(encoding="utf-8")
    for command in (
        ("rm", "-q", "pyproject.toml"),
        ("commit", "-qm", "no version file"),
        ("tag", "v0.2.4"),
    ):
        subprocess.run(("git", *command), cwd=root, check=True, capture_output=True)
    _commit_version_file(root, current, "the current baseline")

    report = doc_check.analyze(root)

    assert report.errors == []
    assert any("v0.2.4" in message for message in report.declined), report.declined


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


# --- the ruff cache, which the local gate must not read ----------------------
#
# isort resolves a first-party import by probing the full dotted path under the
# `src` roots, so one file's verdict depends on whether another file exists,
# while ruff's cache keys a result to the linted file's mtime and permission
# bits alone. Deleting a module invalidates nothing, so `make check` replays a
# clean verdict on a tree CI's fresh checkout fails (`PL-QSJM`).


def _ruffed(root: Path, *, check: str | None, fix: str | None = None) -> Path:
    """A repository whose Makefile runs `ruff check` the given way."""
    recipe = f"\t{check}\n" if check else "\ttrue\n"
    body = f".PHONY: check fix\ncheck:\n{recipe}"
    if fix:
        body += f"fix:\n\t{fix}\n"
    (root / "Makefile").write_text(body, encoding="utf-8")
    return root


def test_a_cache_free_ruff_check_is_quiet(tmp_path: Path) -> None:
    root = _ruffed(_repo(tmp_path), check="uv run ruff check --no-cache .")

    assert _errors(root) == []


def test_a_cached_ruff_check_is_an_error(tmp_path: Path) -> None:
    # The failure this exists for: the gate keeps a stale clean verdict on every
    # file importing a module that has since been deleted, and passes where CI
    # fails.
    root = _ruffed(_repo(tmp_path), check="uv run ruff check .")

    errors = _errors(root)

    assert any("without `--no-cache`" in m for m in errors)


def test_the_error_names_the_line_and_the_command(tmp_path: Path) -> None:
    # A reader has to be able to go straight to it; naming the rule alone would
    # make them search a file whose recipes are mostly comment.
    root = _ruffed(_repo(tmp_path), check="uv run ruff check .")

    joined = " ".join(_errors(root))

    assert "Makefile:3" in joined
    assert "uv run ruff check ." in joined


def test_the_fixing_half_is_held_to_it_too(tmp_path: Path) -> None:
    """`make fix` is the invocation where a stale verdict does the most damage.

    A cached clean result makes `--fix` a no-op, so the target reports nothing
    to fix, `make check` agrees, and the import ruff would have rewritten
    reaches CI unsorted.
    """
    root = _ruffed(
        _repo(tmp_path), check="uv run ruff check --no-cache .", fix="uv run ruff check --fix ."
    )

    assert any("without `--no-cache`" in m for m in _errors(root))


def test_ruff_format_check_is_not_swept_in(tmp_path: Path) -> None:
    # `ruff format --check` carries the word but is a different command, and its
    # cache is sound: its output depends only on the file in front of it, so a
    # stale entry needs that file to have changed - which invalidates the entry.
    root = _ruffed(_repo(tmp_path), check="uv run ruff format --check .")

    assert _errors(root) == []


def test_a_makefile_that_runs_no_ruff_check_is_left_alone(tmp_path: Path) -> None:
    # The rule is about how an invocation is spelled, not about whether a
    # checkout ought to have one.
    assert _errors(_ruffed(_repo(tmp_path), check=None)) == []


def test_ci_is_not_held_to_the_flag(tmp_path: Path) -> None:
    """CI has no cache to go stale, so requiring the flag there requires a no-op.

    This is where the rule departs from `check_coverage_gate` above, which holds
    the Makefile and CI to the same command precisely because both run the gate.
    A fresh checkout restores uv's cache and never `.ruff_cache`, so CI's plain
    `ruff check` is the reference answer this rule exists to make the Makefile
    match - not a second site to correct.
    """
    root = _with_workflow(
        _ruffed(_repo(tmp_path), check="uv run ruff check --no-cache ."),
        "name: quality\n\non: [push, pull_request]\n\njobs:\n  checks:\n"
        "    runs-on: ubuntu-latest\n    steps:\n"
        "      - uses: actions/checkout@v7.0.1\n"
        "      - run: uv run ruff check .\n",
    )

    assert _errors(root) == []


def test_this_repository_runs_every_ruff_check_cache_free() -> None:
    # The rule against the real Makefile rather than a fixture: this is the one
    # that would catch the flag being dropped in a tidy-up.
    report = doc_check.Report()
    doc_check.check_ruff_cache(Path(__file__).resolve().parents[2], report)

    assert report.errors == []


# --- gate parity ------------------------------------------------------------


GATING_WORKFLOW = """name: quality

on:
  push:
    branches: [main]
  pull_request:

jobs:
  checks:
    runs-on: ubuntu-latest
    steps:
{steps}"""

SCHEDULED_WORKFLOW = """name: drift

on:
  schedule:
    - cron: '0 6 1 * *'

jobs:
  drift:
    runs-on: ubuntu-latest
    steps:
{steps}"""


def _parity_repo(
    root: Path, *, local: list[str], workflows: dict[str, tuple[str, list[str]]]
) -> Path:
    """A repository whose `check:` target and workflows run the given scripts."""
    for command in local + [step for _, steps in workflows.values() for step in steps]:
        for token in command.split():
            if token.endswith(".py"):
                (root / token).parent.mkdir(parents=True, exist_ok=True)
                (root / token).write_text("", encoding="utf-8")
    recipe = "".join(f"\t{command}\n" for command in local)
    (root / "Makefile").write_text(f".PHONY: check\ncheck:\n{recipe}", encoding="utf-8")
    directory = root / ".github" / "workflows"
    directory.mkdir(parents=True, exist_ok=True)
    for name, (template, steps) in workflows.items():
        body = "".join(f"      - run: {step}\n" for step in steps)
        (directory / name).write_text(template.format(steps=body), encoding="utf-8")
    return root


def _parity(root: Path) -> list[str]:
    report = doc_check.Report()
    doc_check.check_gate_parity(root, report)
    return report.errors


def test_the_two_gates_running_one_set_of_scripts_is_quiet(tmp_path: Path) -> None:
    root = _parity_repo(
        _repo(tmp_path),
        local=["python3 tools/a_check.py", "uv run python tools/b_check.py"],
        workflows={
            "quality.yml": (
                GATING_WORKFLOW,
                ["python3 tools/a_check.py", "uv run python tools/b_check.py"],
            )
        },
    )

    assert _parity(root) == []


def test_how_a_script_is_invoked_is_not_a_drift(tmp_path: Path) -> None:
    """The floor section runs a tool bare and the sync'd half runs it under `uv`.

    Comparing command strings would report every such line as a divergence,
    which is why the set compared is which scripts each gate runs at all.
    """
    root = _parity_repo(
        _repo(tmp_path),
        local=["uv run python tools/a_check.py"],
        workflows={"quality.yml": (GATING_WORKFLOW, ["python3 tools/a_check.py"])},
    )

    assert _parity(root) == []


def test_a_script_only_the_local_gate_runs_is_an_error(tmp_path: Path) -> None:
    # The failure this exists for: a branch pushed without a local `make check`
    # merges green on a tree `make check` would refuse.
    root = _parity_repo(
        _repo(tmp_path),
        local=["python3 tools/a_check.py", "python3 tools/b_check.py"],
        workflows={"quality.yml": (GATING_WORKFLOW, ["python3 tools/a_check.py"])},
    )

    assert any("tools/b_check.py and no workflow" in m for m in _parity(root))


def test_a_script_only_ci_runs_is_an_error_too(tmp_path: Path) -> None:
    # The other direction, and it costs a red CI run after review has started
    # rather than a silent pass.
    root = _parity_repo(
        _repo(tmp_path),
        local=["python3 tools/a_check.py"],
        workflows={
            "quality.yml": (
                GATING_WORKFLOW,
                ["python3 tools/a_check.py", "python3 tools/b_check.py"],
            )
        },
    )

    assert any("runs tools/b_check.py and `make check` does not" in m for m in _parity(root))


def test_a_recorded_asymmetry_is_accepted(tmp_path: Path) -> None:
    """`GATE_ONLY` is where the reason lives, and writing one is the whole ask."""
    root = _parity_repo(
        _repo(tmp_path),
        local=["python3 tools/a_check.py"],
        workflows={
            "quality.yml": (GATING_WORKFLOW, ["python3 tools/a_check.py", "python3 tools/only.py"])
        },
    )
    doc_check.GATE_ONLY["tools/only.py"] = ("ci", "reads the API")
    try:
        assert _parity(root) == []
    finally:
        del doc_check.GATE_ONLY["tools/only.py"]


def test_a_recorded_asymmetry_is_accepted_on_its_own_side_only(tmp_path: Path) -> None:
    """A script recorded as CI-only that turns up missing from CI still fails."""
    root = _parity_repo(
        _repo(tmp_path),
        local=["python3 tools/a_check.py", "python3 tools/only.py"],
        workflows={"quality.yml": (GATING_WORKFLOW, ["python3 tools/a_check.py"])},
    )
    doc_check.GATE_ONLY["tools/only.py"] = ("ci", "reads the API")
    try:
        assert any("tools/only.py and no workflow" in m for m in _parity(root))
    finally:
        del doc_check.GATE_ONLY["tools/only.py"]


def test_a_scheduled_workflow_is_not_the_merge_gate(tmp_path: Path) -> None:
    """A branch can merge without a monthly run ever having looked at it."""
    root = _parity_repo(
        _repo(tmp_path),
        local=["python3 tools/a_check.py", "python3 tools/b_check.py"],
        workflows={
            "quality.yml": (GATING_WORKFLOW, ["python3 tools/a_check.py"]),
            "drift.yml": (SCHEDULED_WORKFLOW, ["python3 tools/b_check.py"]),
        },
    )

    assert any("tools/b_check.py and no workflow" in m for m in _parity(root))


def test_a_second_pull_request_workflow_does_count(tmp_path: Path) -> None:
    """`pr-title.yml` is why: one script's whole coverage is a workflow of its own."""
    root = _parity_repo(
        _repo(tmp_path),
        local=["python3 tools/a_check.py", "python3 tools/title_check.py"],
        workflows={
            "quality.yml": (GATING_WORKFLOW, ["python3 tools/a_check.py"]),
            "pr-title.yml": (GATING_WORKFLOW, ["python3 tools/title_check.py"]),
        },
    )

    assert _parity(root) == []


def test_the_inline_trigger_list_is_read_too(tmp_path: Path) -> None:
    """`on: [push, pull_request]` gates merges exactly as the block form does.

    Reading only the block form would have reported a workflow written this way
    as gating nothing, which is a wrong answer rather than a missing one.
    """
    inline = GATING_WORKFLOW.replace(
        "on:\n  push:\n    branches: [main]\n  pull_request:\n", "on: [push, pull_request]\n"
    )
    root = _parity_repo(
        _repo(tmp_path),
        local=["python3 tools/a_check.py"],
        workflows={
            "quality.yml": (inline, ["python3 tools/a_check.py", "python3 tools/b_check.py"])
        },
    )

    assert any("runs tools/b_check.py and `make check` does not" in m for m in _parity(root))


def test_a_path_that_does_not_exist_is_not_a_gate(tmp_path: Path) -> None:
    """The rule reads the tree, so a `.py` written as an argument is not swept in."""
    root = _parity_repo(
        _repo(tmp_path),
        local=["python3 tools/a_check.py"],
        workflows={"quality.yml": (GATING_WORKFLOW, ["python3 tools/a_check.py"])},
    )
    (root / "Makefile").write_text(
        ".PHONY: check\ncheck:\n\tpython3 tools/a_check.py\n\techo deleted/gone.py\n",
        encoding="utf-8",
    )

    assert _parity(root) == []


def test_third_party_programs_are_left_to_the_checks_that_compare_them(tmp_path: Path) -> None:
    """`ruff`, `mypy`, `pytest` and `uv` are reconciled line by line or not at all.

    `check_coverage_gate` holds the pytest line to CI's and `check_ruff_cache`
    holds the Makefile's `ruff check` to its flag. Sweeping them in here would
    report `uv sync` and `sudo apt-get install` as gates.
    """
    root = _parity_repo(
        _repo(tmp_path),
        local=["uv run mypy", "uv run ruff check --no-cache .", "python3 tools/a_check.py"],
        workflows={
            "quality.yml": (
                GATING_WORKFLOW,
                ["sudo apt-get install -y libegl1", "python3 tools/a_check.py"],
            )
        },
    )

    assert _parity(root) == []


def test_a_recipe_comment_does_not_end_the_target(tmp_path: Path) -> None:
    """This Makefile carries a paragraph of reasoning above almost every command.

    Reading a comment line as the end of the recipe would have found one script
    under `check` where there are fifteen, and reported the rest as CI-only.
    """
    root = _parity_repo(
        _repo(tmp_path),
        local=["python3 tools/a_check.py", "python3 tools/b_check.py"],
        workflows={
            "quality.yml": (
                GATING_WORKFLOW,
                ["python3 tools/a_check.py", "python3 tools/b_check.py"],
            )
        },
    )
    (root / "Makefile").write_text(
        ".PHONY: check\ncheck:\n\tpython3 tools/a_check.py\n"
        "# Why the next line is here, at length.\n#\n# And a second paragraph.\n"
        "\tpython3 tools/b_check.py\n",
        encoding="utf-8",
    )

    assert _parity(root) == []


def test_a_prerequisite_target_counts_as_part_of_the_gate(tmp_path: Path) -> None:
    """`check: sync` here, and what `sync` runs is part of what `make check` runs."""
    root = _parity_repo(
        _repo(tmp_path),
        local=["python3 tools/a_check.py"],
        workflows={
            "quality.yml": (
                GATING_WORKFLOW,
                ["python3 tools/a_check.py", "python3 tools/b_check.py"],
            )
        },
    )
    (root / "Makefile").write_text(
        ".PHONY: sync check\nsync:\n\tpython3 tools/b_check.py\n"
        "check: sync\n\tpython3 tools/a_check.py\n",
        encoding="utf-8",
    )

    assert _parity(root) == []


def test_a_checkout_with_no_workflows_is_left_alone(tmp_path: Path) -> None:
    root = _parity_repo(_repo(tmp_path), local=["python3 tools/a_check.py"], workflows={})

    assert _parity(root) == []


def test_this_repository_runs_one_set_of_scripts_on_both_gates() -> None:
    # The rule against the real tree rather than a fixture: this is the one that
    # catches a check wired into `make check` and never added to CI, which three
    # of them were (`PL-PBP5`).
    report = doc_check.Report()
    doc_check.check_gate_parity(Path(__file__).resolve().parents[2], report)

    assert report.errors == []


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


# Two payloads reach every session at launch and are resent on every turn, and
# until `PL-44DG` nothing counted either: the SessionStart hook's output and
# each skill's description frontmatter. Measured 2026-09-21 they were 4,169 and
# 625 characters against a reported total of 66,773, so the one gauge the
# project consults about resident size was 7.2% low.

SKILLED = """---
name: worked
description: A description a session is shown before it invokes anything.
---

# worked

A body, which loads only once the skill fires.
"""


def _with_skill(root: Path, name: str = "worked", text: str = SKILLED) -> Path:
    directory = root / ".claude" / "skills" / name
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "SKILL.md").write_text(text, encoding="utf-8")
    return root


def _with_digest(root: Path, emits: str = "queue: 3 open\n", exit_code: int = 0) -> Path:
    """A SessionStart hook that emits a known payload."""
    hooks = root / ".claude" / "hooks"
    hooks.mkdir(parents=True, exist_ok=True)
    # Emitted from a file rather than inlined into the script, so the payload
    # reaches stdout byte for byte: a shell quoting the text would be a test
    # of the quoting.
    (hooks / "payload.txt").write_text(emits, encoding="utf-8")
    hook = hooks / "docket-digest.sh"
    hook.write_text(
        f'#!/usr/bin/env bash\ncat "$(dirname "$0")/payload.txt"\nexit {exit_code}\n',
        encoding="utf-8",
    )
    hook.chmod(0o755)
    return root


def test_a_skill_description_is_resident_and_its_body_is_not(tmp_path: Path) -> None:
    """Claude Code lists every skill's description before one has been invoked.

    So the frontmatter loads at launch and the body does not, and counting the
    file would overstate the launch payload by eight times here.
    """
    root = _with_skill(_instructed(_repo(tmp_path)))

    rows = {row.name: row.characters for row in doc_check.measure_resident(root)}

    assert ".claude/skills/worked/SKILL.md (description)" in rows
    assert ".claude/skills/worked/SKILL.md" not in rows
    block = SKILLED.split("---\n")[1].rstrip("\n")
    assert rows[".claude/skills/worked/SKILL.md (description)"] == len(block)


def test_a_skill_file_with_no_frontmatter_is_not_resident(tmp_path: Path) -> None:
    """Nothing is listed for it, so nothing of it loads at launch."""
    root = _with_skill(_instructed(_repo(tmp_path)), text="# worked\n\nA body.\n")

    assert _resident_names(root) == {"CLAUDE.md"}


def test_a_skills_file_that_is_not_a_skill_md_is_not_resident(tmp_path: Path) -> None:
    """A mode file loads when the skill reads it, which is not at launch."""
    root = _with_skill(_instructed(_repo(tmp_path)))
    modes = root / ".claude" / "skills" / "worked" / "modes"
    modes.mkdir()
    (modes / "one.md").write_text("---\nname: x\n---\n\nBody.\n", encoding="utf-8")

    assert ".claude/skills/worked/modes/one.md (description)" not in _resident_names(root)
    assert ".claude/skills/worked/modes/one.md" not in _resident_names(root)


def test_a_widened_skill_description_is_growth_like_any_other(tmp_path: Path) -> None:
    """The half of the undercount a git ref can reproduce, so it is compared."""
    root = _with_skill(_instructed(_repo(tmp_path)))
    _on_main(root)
    _with_skill(root, text=SKILLED.replace("anything.", "anything, " + "D" * 80 + "."))

    report = doc_check.analyze(root)

    assert report.resident is not None
    assert report.resident.growth == 82
    assert any("grew 82 characters" in message for message in report.advisories)


def test_the_session_start_digest_is_counted(tmp_path: Path) -> None:
    """The payload that grows on its own, and that nothing counted.

    It carries the dead-ends list and scales with the store, so it is the one
    component of resident cost that can rise without any edit to an
    instruction file - which is exactly what a size gauge is for.
    """
    root = _with_digest(_instructed(_repo(tmp_path)), emits="branch: main\nqueue: 3 open\n")

    report = doc_check.analyze(root)

    assert report.resident is not None
    assert report.resident.total == len(CLAUDE_BODY) + len("branch: main\nqueue: 3 open\n")
    assert ".claude/hooks/docket-digest.sh (output) 27/2" in doc_check.format_check(report)
    assert report.declined == []


def test_the_digest_is_left_out_of_the_growth_comparison(tmp_path: Path) -> None:
    """A store that grew is not an instruction file that grew.

    `git show <ref>:<path>` returns a hook's source and never its output, so
    there is no baseline for this row. Compared, it would read as growth of
    its whole size on the first run and then forever; left out, the printed
    total is true and the advisory still means what it says.
    """
    root = _with_digest(_instructed(_repo(tmp_path)), emits="short\n")
    _on_main(root)
    _with_digest(root, emits="much longer output " + "L" * 400 + "\n")

    report = doc_check.analyze(root)

    assert report.resident is not None
    assert report.resident.growth == 0
    assert report.resident.total == len(CLAUDE_BODY) + len("much longer output " + "L" * 400 + "\n")
    assert report.advisories == []


def test_a_digest_that_will_not_run_is_declined_rather_than_dropped(tmp_path: Path) -> None:
    """A total short by four thousand characters with nothing saying so is the
    partial reading handed over as a complete one that the apparatus floor
    refuses."""
    root = _with_digest(_instructed(_repo(tmp_path)), emits="anything\n", exit_code=1)

    report = doc_check.analyze(root)

    assert report.resident is not None
    assert report.resident.total == len(CLAUDE_BODY)
    assert any("docket-digest.sh adds to every session" in m for m in report.declined)
    assert "1 not checked" in doc_check.format_check(report)


def test_a_tree_with_no_digest_hook_claims_nothing_about_one(tmp_path: Path) -> None:
    """Most projects have no such hook; that is not a reading that went missing."""
    report = doc_check.analyze(_instructed(_repo(tmp_path)))

    assert report.declined == []
    assert report.resident is not None
    assert report.resident.runtime == ()


def test_this_repository_still_has_the_hook_the_count_reads(tmp_path: Path) -> None:
    """A rename would drop four thousand characters out of the total in silence.

    `measure_digest` returns `None` for a hook that is not there, and the
    declined line is guarded on the file existing - correctly, since a project
    without one is owed no explanation. That leaves a rename here invisible,
    and this is the assertion that catches it. Paired with the settings entry,
    because a hook that exists and is not registered reaches no session
    either.
    """
    repo = Path(__file__).resolve().parents[2]

    assert (repo / doc_check.DIGEST_HOOK).is_file()
    settings = (repo / ".claude" / "settings.json").read_text(encoding="utf-8")
    assert doc_check.DIGEST_HOOK in settings
    assert "SessionStart" in settings


# --- instructions loaded on demand -------------------------------------------


SKILL_BODY = """---
name: thing
description: Do the thing.
---

# thing

One line.
"""


def _on_demand_names(root: Path) -> set[str]:
    return {row.name for row in doc_check.measure_on_demand(root)}


def _skilled(root: Path, name: str = "thing", body: str = SKILL_BODY) -> Path:
    directory = root / ".claude" / "skills" / name
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "SKILL.md").write_text(body, encoding="utf-8")
    return root


def test_a_skill_is_measured_on_demand_and_never_as_resident(tmp_path: Path) -> None:
    """The blind spot this exists to close: a skill loads, and nothing counted it."""
    root = _skilled(_instructed(_repo(tmp_path)))

    assert ".claude/skills/thing/SKILL.md" in _on_demand_names(root)
    assert ".claude/skills/thing/SKILL.md" not in _resident_names(root)


def test_a_rule_is_counted_in_exactly_one_of_the_two_sets(tmp_path: Path) -> None:
    """`paths:` decides which set a rule lands in, and nothing lands in both.

    Double-counting would not fail anything - neither total gates a build - so
    only a test says whether the two numbers can be read side by side at all.
    """
    root = _instructed(_repo(tmp_path), scoped=SCOPED_RULE, always=UNSCOPED_RULE)

    assert ".claude/rules/scoped.md" in _on_demand_names(root)
    assert ".claude/rules/scoped.md" not in _resident_names(root)
    assert ".claude/rules/always.md" in _resident_names(root)
    assert ".claude/rules/always.md" not in _on_demand_names(root)


def test_the_worker_instructions_are_measured_on_demand(tmp_path: Path) -> None:
    """A worker run loads them in full; no other session loads them at all."""
    root = _instructed(_repo(tmp_path))
    (root / "docs" / "worker.md").write_text("# Worker\n\nOne line.\n", encoding="utf-8")

    assert "docs/worker.md" in _on_demand_names(root)


def test_a_tree_with_nothing_loadable_on_demand_reports_nothing(tmp_path: Path) -> None:
    assert doc_check.analyze(_instructed(_repo(tmp_path))).on_demand is None


def test_a_rule_routed_into_a_skill_moves_both_totals(tmp_path: Path) -> None:
    """The exact move the resident advisory could not see (`PL-JQVB`).

    Routing a rule out of `CLAUDE.md` and into a skill is the answer
    `CLAUDE.md`'s four dispositions prefer, so nothing here is an advisory. The
    defect was that only one side of it was ever reported: the resident total
    fell and the text it held reappeared nowhere, which reads as a deletion.
    """
    root = _skilled(_instructed(_repo(tmp_path), claude=CLAUDE_BODY + RULE_LINE * 2))
    _on_main(root)
    (root / "CLAUDE.md").write_text(CLAUDE_BODY, encoding="utf-8")
    _skilled(root, body=SKILL_BODY + RULE_LINE * 2)

    report = doc_check.analyze(root)

    assert report.resident is not None
    assert report.on_demand is not None
    assert report.resident.growth == -2 * len(RULE_LINE)
    assert report.on_demand.growth == 2 * len(RULE_LINE)
    assert report.on_demand.deltas() == [(".claude/skills/thing/SKILL.md", 2 * len(RULE_LINE))]


def test_the_two_totals_are_reported_separately_and_never_summed(tmp_path: Path) -> None:
    """A skill that never fires costs a session nothing, so one figure would lie."""
    root = _skilled(_instructed(_repo(tmp_path)))

    rendered = doc_check.format_check(doc_check.analyze(root))

    assert "resident instructions:" in rendered
    assert "instructions loaded on demand:" in rendered


def test_this_repository_measures_its_own_skill_on_demand(tmp_path: Path) -> None:
    """Run against the real tree: the `docket` skill is the text this was built for."""
    root = Path(doc_check.__file__).resolve().parent.parent
    on_demand = doc_check.analyze(root).on_demand

    assert on_demand is not None
    measured = {row.name: row for row in on_demand.files}
    assert ".claude/skills/docket/SKILL.md" in measured
    assert ".claude/rules/apparatus-standard.md" in measured
    assert ".claude/rules/instruction-writing.md" not in measured


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


def test_frontmatter_is_not_scanned_for_math_delimiters(tmp_path: Path) -> None:
    """A `verify:` regex that escapes a parenthesis is a shell command, not LaTeX.

    GitHub hides frontmatter or shows it as a table, so there is no math there
    to render wrongly. Scanning it failed the run on `PL-6194`'s command and
    the only repair available was to contort a working regex (`PL-WTQ1`).
    """
    body = (
        "---\n"
        "id: PL-6194\n"
        "verify: uv run pytest && ! grep -rEq '=\\([a-z]*\\),?$' src/\n"
        "---\n"
        "\n"
        "**Problem.** x\n"
    )

    assert _math_errors(tmp_path / "repo", "docs/items/PL-6194-x.md", body) == []


def test_math_in_the_body_below_frontmatter_is_still_reported(tmp_path: Path) -> None:
    """The skip is the frontmatter's span and nothing else.

    A fix that silenced the whole file would be worse than the defect: the
    body of an item renders on GitHub like any other prose.
    """
    body = "---\nid: PL-6194\n---\n\nThe step \\(\\Delta t\\) is explicit.\n"

    errors = _math_errors(tmp_path / "repo", "docs/items/PL-6194-x.md", body)

    assert len(errors) == 2
    assert all("docs/items/PL-6194-x.md:5" in error for error in errors)


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


def test_a_gate_group_holding_exactly_one_entry_may_say_so_in_the_singular(tmp_path: Path) -> None:
    """`1 entry` has to count, or a singleton group cannot be written at all.

    Requiring the plural left a one-item post-freeze addition with no correct
    form: `1 entries` is not English, and dropping the count stops the line
    being read as a heading, which silently folds its entry into the group
    above (`PL-L0K3`). Both halves are asserted here - the singular heading is
    accepted, and it is still held to what follows it.
    """
    roadmap = GATE_ROADMAP.replace(
        "- PL-HHHH (S) The fifth thing",
        "- PL-HHHH (S) The fifth thing\n\n"
        "*Added later — 1 entry:*\n\n"
        "- PL-JJJJ (S) The sixth thing",
    )

    assert _gate_errors(tmp_path, roadmap) == []


def test_a_singular_gate_group_heading_is_still_held_to_its_count(tmp_path: Path) -> None:
    """Accepting `entry` must not make the count unenforced under it."""
    roadmap = GATE_ROADMAP.replace(
        "- PL-HHHH (S) The fifth thing",
        "- PL-HHHH (S) The fifth thing\n\n"
        "*Added later — 1 entry:*\n\n"
        "- PL-JJJJ (S) The sixth thing\n"
        "- PL-KKKK (S) The seventh thing",
    )

    errors = _gate_errors(tmp_path, roadmap)

    assert any("says 1 entries, but 2 follow it" in error for error in errors)


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


def test_a_count_in_a_gate_subsection_heading_is_refused(tmp_path: Path) -> None:
    """A heading sits outside the only range `_gate_groups` reads.

    The frozen list stops at the first `###`, so a number written into a
    subsection heading below the gate is checked by nothing while reading
    exactly like the ones that are. `ROADMAP.md`'s declined subsection
    carried one through twenty hand edits to 228 against 128 entries listed
    and validated identically at 174, 191 and 999 (`PL-4RHP`).
    """
    roadmap = GATE_ROADMAP.replace(
        "### Definition of done",
        "### Declined to Gate 1 on the refilling-queue ground — 7 entries\n\n"
        "Deferred because pulling it in would refill the gate.\n\n"
        "- PL-ZZZZ (S) The deferred thing\n\n### Definition of done",
        1,
    )

    errors = _gate_errors(tmp_path, roadmap)

    assert any("states 7 entries, and nothing checks it" in error for error in errors)


def test_a_gate_subsection_heading_counting_one_entry_is_refused_too(tmp_path: Path) -> None:
    """The singular is the obvious way round, so it is read as a count.

    `ENTRY_COUNT_RE` is plural-only on purpose - it scans prose, where "the
    one entry a user cannot set" is a sentence. A heading holds no sentences,
    so the two regexes part company here and this pins which one applies.
    """
    roadmap = GATE_ROADMAP.replace(
        "### Definition of done",
        "### Declined to Gate 1 on the refilling-queue ground — 1 entry\n\n"
        "Deferred because pulling it in would refill the gate.\n\n"
        "- PL-ZZZZ (S) The deferred thing\n\n### Definition of done",
        1,
    )

    errors = _gate_errors(tmp_path, roadmap)

    assert any("states 1 entry, and nothing checks it" in error for error in errors)


def test_a_gate_subsection_stating_its_count_in_prose_is_left_alone(tmp_path: Path) -> None:
    """Prose keeps the reader's exemption; only the heading loses it.

    A heading carries no date and counts what is below it, so it goes stale on
    the next addition. A sentence can be a dated fact that must never change,
    which is why `check_gate_counts` refuses to guess at prose - and a check
    firing on a correct document every run is the failure this one would have.
    """
    roadmap = GATE_ROADMAP.replace(
        "### Definition of done",
        "### Declined to Gate 1 on the refilling-queue ground\n\n"
        "Deferred 2026-08-25, when this gate held three entries.\n\n"
        "- PL-ZZZZ (S) The deferred thing\n\n### Definition of done",
        1,
    )

    assert _gate_errors(tmp_path, roadmap) == []


# --- the self-cleared group, held to Required scope -------------------------

#: The fixture's gate with a self-cleared group holding one entry, and its
#: `Required scope` declaring exactly that entry - the arrangement the rule asks
#: for, which the two tests after the quiet one each break in one direction.
SELF_CLEARED_ROADMAP = VERSIONED_GATE_ROADMAP.replace(
    "- PL-HHHH (S) The fifth thing\n",
    "- PL-HHHH (S) The fifth thing\n\n"
    "**Cleared by v0.4.0 itself — one entry**\n\n"
    "- PL-JJJJ (S) The milestone's own debt\n",
).replace(
    "### Required scope\n\n- Something.", "### Required scope\n\n- Something (queue item PL-JJJJ)."
)


def _self_cleared(tmp_path: Path, roadmap: str) -> list[str]:
    return [e for e in _errors(_repo(tmp_path, roadmap=roadmap)) if "Cleared by v0.4.0 itself" in e]


def test_a_self_cleared_group_holding_what_required_scope_declares_is_quiet(tmp_path: Path) -> None:
    assert _self_cleared(tmp_path, SELF_CLEARED_ROADMAP) == []


def test_a_required_scope_entry_outside_the_self_cleared_group_is_reported(tmp_path: Path) -> None:
    """`PL-J6HP`: v0.6.0 filed `PL-CNCF` and `PL-PGZF` under "Cleared before".

    `#862` declared both in `Required scope` after `#850` had grouped the list,
    so the list told a reader the milestone did not clear two entries that the
    rule - and `bin/docket wave` - said it did. Every count agreed, because
    each group heading counted the entries under it correctly.
    """
    roadmap = SELF_CLEARED_ROADMAP.replace(
        "(queue item PL-JJJJ).", "(queue items PL-JJJJ and PL-DDDD)."
    )

    errors = _self_cleared(tmp_path, roadmap)

    assert len(errors) == 1
    assert "PL-DDDD is declared in v0.4.0's Required scope" in errors[0]
    assert 'under "Stops new debt being introduced — three entries:"' in errors[0]


def test_an_entry_under_the_self_cleared_group_that_scope_does_not_declare_is_reported(
    tmp_path: Path,
) -> None:
    """The other direction: the group claiming an entry the rule does not give it."""
    roadmap = SELF_CLEARED_ROADMAP.replace(" (queue item PL-JJJJ).", ".")

    errors = _self_cleared(tmp_path, roadmap)

    assert len(errors) == 1
    assert "PL-JJJJ sits under" in errors[0]
    assert "Required scope does not declare it" in errors[0]


def test_the_gate_rules_read_the_gate_wave_reads(tmp_path: Path) -> None:
    """`PL-J6HP`: one function names the current gate, for `wave` and here alike.

    They used to find it apart - `wave` in the release train's order, the gate
    rules in version order - and the two orders differ once a section recording
    a gate has no timeline row. v0.3.5's has none here, so the train puts it
    after v0.4.0, and every reader must hold the queue to v0.4.0's list: read in
    version order, `PL-QQQQ` looked placed by a list `wave` never reports.

    The re-entry rule is the reader held here, since the disposition rule moved
    into `bin/docket check` (`PL-WD5Z`), and that one reads the same
    `baseline_gate` through `MilestoneStates.gate`.
    """
    from docket.roadmap import milestone_states, wave

    roadmap = VERSIONED_GATE_ROADMAP.replace(
        "## Next milestone: v0.4.0",
        "## v0.3.5 - a gate the timeline never placed\n\n"
        "### Debt gate: the frozen list\n\n"
        "- PL-QQQQ (S) On this list and no other\n\n"
        "## Next milestone: v0.4.0",
    )
    root = _repo(tmp_path, roadmap=roadmap)
    _queue_item(root, "PL-QQQQ", classes="safety")

    plan = wave(roadmap, "0.2.5", frozenset(), frozenset(), {})
    states = milestone_states(roadmap)
    advisories = _reentry_advisories(root)

    assert plan.gate is not None and plan.gate.milestone.version == (0, 4, 0)
    assert states.gate is not None and states.gate.version == (0, 4, 0)
    assert any("v0.4.0's frozen list" in a and "PL-QQQQ" in a for a in advisories)


# --- gate re-entries, the queue read against the frozen list -----------------
#
# `check_gate_counts` above holds a frozen list's arithmetic to itself. These
# hold its *membership* to the queue: an open `safety`- or `science`-classed
# item re-enters the current gate regardless of when it was found, and until
# `PL-KTKP` nothing reconciled the two, so eleven qualifying items sat unlisted
# while every count in the file agreed.


def _queue_item(
    root: Path,
    identifier: str,
    *,
    classes: str,
    status: str = "ready",
    not_delegable: str = "",
    deferred_from: str = "",
) -> None:
    """Write one item into the fixture repository's store."""
    store = root / "docs" / "items"
    store.mkdir(parents=True, exist_ok=True)
    withheld = f"not-delegable: {not_delegable}\n" if not_delegable else ""
    withheld += f"deferred-from: {deferred_from}\n" if deferred_from else ""
    (store / f"{identifier}-demo.md").write_text(
        "---\n"
        f"id: {identifier}\n"
        "title: A thing\n"
        "priority: P1\n"
        "effort: S\n"
        f"status: {status}\n"
        f"classes: {classes}\n"
        f"{withheld}"
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


def test_a_deferred_safety_item_still_re_enters_the_gate(tmp_path: Path) -> None:
    """A recorded deferral answers `bin/docket check`'s disposition rule and not this check.

    `PL-R0Q0`: the advisory offered a deferral as a third remedy and then
    refused it, so `PL-MN4J` and four `anticipated` area-model findings - each
    deferred in v0.5.0's `### Declined to Gate ...` subsection with its reason
    written out - advised on every `make check` under text that named no
    remedy it would accept. The refusal is the correct half: "The gate is a
    snapshot" ends by making `safety` and `science` not deferrable, and the
    frozen list takes a post-freeze re-entry with its date, as this gate's own
    `PL-GS3R` shows. It was the offer that had to go.

    `PL-83LS` then took the four out of this check's reach entirely, on their
    `anticipated` class rather than on their deferral - the test below pins
    that - and `PL-R7XK` placed `PL-MN4J` in `Required scope`. Neither touches
    what this test holds: a deferral, on its own, still leaves the item named.
    """
    root = _repo(tmp_path, roadmap=VERSIONED_GATE_ROADMAP)
    _queue_item(
        root,
        "PL-ZZZZ",
        classes="safety, ux",
        deferred_from="v0.4.0 - the milestone creates the display it is about",
    )

    advisories = _reentry_advisories(root)

    assert len(advisories) == 1
    assert "PL-ZZZZ (safety)" in advisories[0]
    assert "or defer it with a reason" not in advisories[0]


def test_an_anticipated_safety_item_is_quiet(tmp_path: Path) -> None:
    """`PL-83LS`'s carve-out: an unbuilt hazard is not debt this gate can clear.

    `ROADMAP.md` § "The gate is a snapshot, not a moving target" makes an
    `anticipated` `safety` or `science` finding not debt until the milestone
    that creates the hazard builds it (project owner, 2026-09-16, ratified).
    Ten area-model findings were in exactly this state and could take neither
    remedy the advisory named - nothing to clear, and a `Required scope` two
    milestones away - so it fired on every `make check` with no state a session
    could reach.

    The `blocked` status is load-bearing rather than incidental scenery, since
    `PL-ZF2G`: it is the half of the pair that lets the exemption end, and the
    two tests below take the other side of each half.
    """
    root = _repo(tmp_path, roadmap=VERSIONED_GATE_ROADMAP)
    _queue_item(root, "PL-ZZZZ", classes="safety, anticipated", status="blocked")

    assert _reentry_advisories(root) == []


def test_an_anticipated_safety_item_is_reported_once_it_is_no_longer_blocked(
    tmp_path: Path,
) -> None:
    """`PL-ZF2G`: the carve-out expires with the wait it was granted for.

    On the class alone the exclusion never stopped, so a finding written against
    an unbuilt milestone stayed invisible to the gate after that milestone
    shipped - a rule about *when* a hazard begins, unable to notice the one
    event it exists for. `status: blocked` is what an item stops saying once its
    wait is over, so promoting it off that status is what returns it to the gate
    (project owner, 2026-09-16, ratified).
    """
    root = _repo(tmp_path, roadmap=VERSIONED_GATE_ROADMAP)
    _queue_item(root, "PL-ZZZZ", classes="safety, anticipated", status="ready")

    advisories = _reentry_advisories(root)

    assert len(advisories) == 1
    assert "PL-ZZZZ (safety)" in advisories[0]


def test_a_blocked_safety_item_without_the_class_is_still_reported(tmp_path: Path) -> None:
    """The other half of the pair: `blocked` on its own exempts nothing.

    Most blocked items are merely sequenced - the blocker says what to do first,
    not that the hazard is unbuilt - which is `checks.py`'s "A blocked item where
    something is already wrong is the opposite case". Exempting on status alone
    would hand the carve-out to every one of them, and the class is what draws
    the distinction the status cannot.
    """
    root = _repo(tmp_path, roadmap=VERSIONED_GATE_ROADMAP)
    _queue_item(root, "PL-ZZZZ", classes="safety, ux", status="blocked")

    advisories = _reentry_advisories(root)

    assert len(advisories) == 1
    assert "PL-ZZZZ (safety)" in advisories[0]


def test_a_plain_safety_item_beside_an_anticipated_one_is_still_reported(tmp_path: Path) -> None:
    """The other direction, which is what keeps the carve-out narrow.

    The cost recorded with the decision is that `anticipated` now carries weight
    it did not: a `safety` item wrongly classed goes invisible to the gate,
    which is `PL-MVC2`'s shape. So the exclusion has to turn on the class being
    *present*, never on anything inferred from the item beside it.
    """
    root = _repo(tmp_path, roadmap=VERSIONED_GATE_ROADMAP)
    _queue_item(root, "PL-ZZZZ", classes="safety, anticipated", status="blocked")
    _queue_item(root, "PL-YYYY", classes="safety, ux")

    advisories = _reentry_advisories(root)

    assert len(advisories) == 1
    assert "PL-YYYY (safety)" in advisories[0]
    assert "PL-ZZZZ" not in advisories[0]
    assert "1 open item" in advisories[0]


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


# --- reading the right table, and surviving a token glob cannot parse --------


def test_a_decoy_table_above_the_provenance_table_is_named_as_the_cause(tmp_path: Path) -> None:
    """One accurate error instead of one misleading error per stored constant.

    `PL-ZBZZ` and `PL-K997`: `table_rows` yields the rows of the *first* table
    under a heading, and `## Parameter provenance` is hundreds of lines of
    prose, so any table written above the real one displaced it. The check then
    walked the wrong rows and reported a missing-row error for every constant -
    each true of the table it read, each false of the document, and the remedy
    they suggested was to add rows to a citation list. Two sessions met it
    three days apart and both resolved it by not writing a table.
    """
    decoy = "\n".join(
        [
            "| Source | What it establishes |",
            "| --- | --- |",
            "| Yasuda et al. 1991 | Wash-in on volunteers |",
            "",
        ]
    )
    model = MODEL.replace(
        "| Parameter | Selected value | Unit | Source (data file · key path) |",
        decoy + "| Parameter | Selected value | Unit | Source (data file · key path) |",
        1,
    )
    errors = _errors(_repo(tmp_path, model=model))

    assert any("carry no provenance header" in error for error in errors), errors
    assert any("Source | What it establishes" in error for error in errors), errors
    # The misleading half is gone: no per-constant row errors are raised.
    assert not any("no provenance row for" in error for error in errors), errors


def test_a_table_below_the_provenance_table_does_not_displace_it(tmp_path: Path) -> None:
    """The fix must not trade one positional rule for another."""
    trailer = "\n| Note | Value |\n| --- | --- |\n| A | B |\n"
    model = MODEL.replace("\n## Known limitations", trailer + "\n## Known limitations", 1)

    assert not any("provenance header" in error for error in _errors(_repo(tmp_path, model=model)))


def test_an_absolute_glob_citation_is_reported_rather_than_raised(tmp_path: Path) -> None:
    """A citation `glob` refuses to parse is a finding about that line, not a crash.

    `PL-0M7L`: `Path.glob` raises `NotImplementedError` for a non-relative
    pattern, and the call was unguarded - so one such token aborted the whole
    run on a traceback and the checker reported nothing at all about the
    several hundred citations around it. The failure also looked like a broken
    tool rather than a broken line.
    """
    model = MODEL + "\nEverything under `/docs/*.md` is checked.\n"
    root = _repo(tmp_path, model=model)

    report = doc_check.analyze(root)  # must not raise

    assert any("/docs/*.md" in error for error in report.errors), report.errors


#: `ROADMAP` with one scoped milestone section, so the two scope headings exist
#: to be compared. The base fixture carries a timeline and nothing else.
SCOPED_SECTION_ROADMAP = ROADMAP.replace(
    "## Planned milestones",
    """## v0.4.0 - the teachable case

### Goal

Make one case observable.

### Required scope

- **A displayed clinical unit** (queue item PL-MNPQ).

### Definition of done

The learner can run one case.

### Explicitly out of scope for v0.4.0

- Horizontal panning of the chart (queue item PL-Z7LY).

## Planned milestones""",
)


def test_a_milestone_whose_two_scope_headings_agree_is_quiet(tmp_path: Path) -> None:
    """The correct form stays silent, or the check gets disabled."""
    root = _repo(tmp_path, roadmap=SCOPED_SECTION_ROADMAP)

    assert not [e for e in _errors(root) if "in scope and out of it" in e]
    assert not [a for a in _advisories(root) if "Required scope" in a]


def test_an_id_under_both_scope_headings_is_an_error(tmp_path: Path) -> None:
    """The exact half of `PL-NBCS`'s rule: the section contradicts itself.

    No judgment in it - the same id is named as scope and as excluded - so it
    fails hard rather than advising. This is the shape a later edit would
    reintroduce after the exclusion was moved, which is what makes it the rule
    that holds the fix in place.
    """
    roadmap = SCOPED_SECTION_ROADMAP.replace(
        "- **A displayed clinical unit** (queue item PL-MNPQ).",
        "- **A displayed clinical unit** (queue item PL-MNPQ).\n"
        "- **Horizontal panning** (queue item PL-Z7LY).",
    )
    root = _repo(tmp_path, roadmap=roadmap)

    errors = [e for e in _errors(root) if "in scope and out of it" in e]
    assert len(errors) == 1
    assert "PL-Z7LY" in errors[0]


def test_exclusion_language_in_a_scope_bullet_is_an_advisory(tmp_path: Path) -> None:
    """The keyword half, and the only rule that catches the original shape.

    Where the exclusion is written *only* in the scope bullet there is no
    contradiction to find, so the error above is silent and this is what fires.
    It is a keyword guess, admissible here because it changes no placement and
    only asks a person to move a sentence - the same guess was refused inside
    `docket`'s ranker, where a missed phrasing would print a wrong marking.
    """
    roadmap = SCOPED_SECTION_ROADMAP.replace(
        "- **A displayed clinical unit** (queue item PL-MNPQ).",
        "- **A displayed clinical unit** (queue item PL-MNPQ).\n"
        "- **Stage 3 is not in scope** (queue item PL-WXYZ): it stays at\n"
        "  Gate 1, because only v0.5.0 needs it.",
    )
    root = _repo(tmp_path, roadmap=roadmap)

    advisories = [a for a in _advisories(root) if "reads as scope" in a]
    assert len(advisories) == 1
    assert "PL-WXYZ" in advisories[0]
    assert not [e for e in _errors(root) if "in scope and out of it" in e]


def test_an_exclusion_sentence_naming_no_declared_id_is_left_alone(tmp_path: Path) -> None:
    """The half of the same rule `PL-HWW1` retired, and why it was retired.

    The advisory says the bullet's ids are read as scope, and that was true of
    every id under the heading until membership became a declaration. An id in
    the *sentence* now places nothing, so the same warning on this shape would
    report a hazard that no longer exists - and an advisory that fires without
    changing a decision costs attention on every run and trains a reader to
    skim the line where the real one appears.

    The entry still declares its own member, so it is not the undeclared-entry
    error either. What is left is a sentence a person may want to move, which
    is not a thing to fail a run over.
    """
    roadmap = SCOPED_SECTION_ROADMAP.replace(
        "- **A displayed clinical unit** (queue item PL-MNPQ).",
        "- **A displayed clinical unit** (queue item PL-MNPQ). Stage 3 is\n"
        "  **not** in scope: it is queue item PL-WXYZ and stays at Gate 1.",
    )
    root = _repo(tmp_path, roadmap=roadmap)

    assert not [a for a in _advisories(root) if "reads as scope" in a]
    assert not [e for e in _errors(root) if "Required scope" in e]


def test_a_required_scope_entry_declaring_no_queue_item_is_an_error(tmp_path: Path) -> None:
    """Membership is declared, so an entry that declares nothing places nothing.

    This is what holds the declaration rule in place. Without it the next entry
    written without a slot is scope to every reader and to no tool, silently -
    which is the shape `PL-HWW1` removed from the other direction, where an id
    cited in prose was scope to the tool and to no reader.
    """
    roadmap = SCOPED_SECTION_ROADMAP.replace(
        "- **A displayed clinical unit** (queue item PL-MNPQ).",
        "- **A displayed clinical unit** (queue item PL-MNPQ).\n"
        "- **A second thing this milestone requires**, described at length.",
    )
    root = _repo(tmp_path, roadmap=roadmap)

    errors = [e for e in _errors(root) if "declares no queue item" in e]
    assert len(errors) == 1
    assert "v0.4.0" in errors[0]


def test_a_section_declaring_nothing_at_all_is_not_held_to_the_rule(tmp_path: Path) -> None:
    """v0.1.0 and v0.2.0 were written before the queue existed.

    Their entries name no ids because there were none to name, and they place
    nothing under either reading. A rule that failed them would be asking for
    ids to be invented for a shipped milestone, so the rule holds a section to
    what that section already does: it fires only where the other entries
    declare.
    """
    roadmap = SCOPED_SECTION_ROADMAP.replace(
        "- **A displayed clinical unit** (queue item PL-MNPQ).",
        "- Add an alveolar compartment driven by alveolar ventilation.\n"
        "- Document the equations, units and assumptions.",
    )
    root = _repo(tmp_path, roadmap=roadmap)

    assert not [e for e in _errors(root) if "declares no queue item" in e]


def test_a_declared_scope_id_the_store_does_not_hold_is_an_error(tmp_path: Path) -> None:
    """A declaration places an item, so a typo in one places nothing.

    The same reading `GateStatus.unknown_ids` takes of a frozen list, applied
    to the structure beside it: an id no item answers to leaves the milestone's
    scope smaller than the document says, with nothing reporting the gap.
    """
    roadmap = SCOPED_SECTION_ROADMAP.replace(
        "- **A displayed clinical unit** (queue item PL-MNPQ).",
        "- **A displayed clinical unit** (queue item PL-MNPQ).\n"
        "- **A unit nobody filed** (queue item PL-ZZZZ).",
    )
    root = _repo(tmp_path, roadmap=roadmap)
    _queue_item(root, "PL-MNPQ", classes="feature")

    errors = [e for e in _errors(root) if "the queue does not hold" in e]
    assert len(errors) == 1
    assert "PL-ZZZZ" in errors[0]
    assert "PL-MNPQ" not in errors[0]


def _with_tests(root: Path, *names: str) -> Path:
    """Give a fixture repository a test suite defining `names`."""
    suite = root / "tests" / "unit"
    suite.mkdir(parents=True, exist_ok=True)
    body = "\n\n".join(f"def {name}() -> None:\n    pass" for name in names)
    (suite / "test_demo.py").write_text(body + "\n", encoding="utf-8")
    return root


def test_a_named_test_that_exists_is_quiet(tmp_path: Path) -> None:
    """The correct form stays silent, or the check gets disabled."""
    model = MODEL + "\n\nThe invariant is held by `test_the_thing_holds`.\n"
    root = _with_tests(_repo(tmp_path, model=model), "test_the_thing_holds")

    assert not [e for e in _errors(root) if "test_the_thing_holds" in e]


def test_a_named_test_that_no_longer_exists_is_an_error(tmp_path: Path) -> None:
    """A renamed or deleted test leaves the sentence reading as it did.

    That is the whole reason the check exists: `docs/MODEL.md` asserts an
    invariant or a mitigation is *held* by something, and the assertion decays
    silently when the something is gone.
    """
    model = MODEL + "\n\nThe invariant is held by `test_renamed_away`.\n"
    root = _with_tests(_repo(tmp_path, model=model), "test_something_else")

    errors = [e for e in _errors(root) if "test_renamed_away" in e]
    assert len(errors) == 1
    assert "unverified until the name resolves" in errors[0]


def test_no_test_directory_declines_rather_than_failing(tmp_path: Path) -> None:
    """A checkout with no suite has not disproved the citation, so it declines.

    `_repo` builds no `tests/`, which is the shape a bare or truncated checkout
    has. Erroring there would fail a citation nobody could have checked, and
    "not checked" and "wrong" are different results.
    """
    model = MODEL + "\n\nThe invariant is held by `test_absent_suite`.\n"
    root = _repo(tmp_path, model=model, tests=False)
    report = doc_check.analyze(root)

    assert not [e for e in report.errors if "test_absent_suite" in e]
    assert any("no test directory was found" in d for d in report.declined)


# --- bound families, the question that comes before "does the name resolve" --
#
# `check_named_tests` asks whether a name resolves. These cover the prior
# question - whether the statement named anything at all - which is the one a
# specification written as prose cannot answer about itself (`PL-4FBP`). Four
# of them are the whole member rule: names its entity, declares none against an
# open item, declares none against an item that cannot carry the debt, names
# nothing. The fifth is the family going missing, which must not read as a pass.


def _family_model(held_by: str) -> str:
    """The fixture document with its one bound-family member's cell replaced."""
    return MODEL.replace(f"`{FAMILY_TEST}`", held_by)


def _family_repo(tmp_path: Path, held_by: str, items: dict[str, str] | None = None) -> Path:
    """A fixture repository whose bound-family member reads `held_by`.

    `items` maps an id to a status and builds a store when given; without one
    the checkout has no queue, which is what a declared absence cannot be
    resolved against.
    """
    root = _repo(tmp_path, model=_family_model(held_by))
    if items is None:
        return root
    (root / "docket.toml").write_text('items_dir = "docs/items"\n', encoding="utf-8")
    store = root / "docs" / "items"
    store.mkdir(parents=True, exist_ok=True)
    for identifier, status in items.items():
        (store / f"{identifier}-demo.md").write_text(
            f"---\nid: {identifier}\ntitle: Demo\npriority: P2\neffort: S\n"
            f"status: {status}\nadded: 2026-09-06\n---\n\n"
            "**Problem.** A thing.\n**Why it matters.** It does.\n**Done when.** Fixed.\n",
            encoding="utf-8",
        )
    return root


def _family_errors(root: Path) -> list[str]:
    return [e for e in _errors(root) if "Reasonably foreseeable misuse" in e]


def test_a_family_member_that_names_its_entity_is_quiet(tmp_path: Path) -> None:
    """The conforming form stays silent, or the check gets disabled."""
    assert _family_errors(_family_repo(tmp_path, f"`{FAMILY_TEST}`")) == []


def test_a_family_member_declaring_no_test_yet_against_an_open_item_is_quiet(
    tmp_path: Path,
) -> None:
    """A declared absence is a forward reference to work, and passes as one.

    This is the half the hazard table's own sentence lacked: it said a row may
    say plainly that it has none, and left "plainly" to the reader. The fixed
    parenthesis is what lets a script tell a declared absence from a forgotten
    link.
    """
    root = _family_repo(tmp_path, "no test yet (`PL-8888`)", items={"PL-8888": "ready"})

    assert _family_errors(root) == []


def test_a_family_member_declaring_no_test_yet_against_a_closed_item_is_an_error(
    tmp_path: Path,
) -> None:
    """Closing the item without adding the link turns the exemption into a hole.

    The forward reference was the whole of what made the absence acceptable, so
    it has to expire with the item rather than outlive it silently.
    """
    root = _family_repo(tmp_path, "no test yet (`PL-8888`)", items={"PL-8888": "done"})
    errors = _family_errors(root)

    assert len(errors) == 1
    assert "which is done" in errors[0]


def test_a_family_member_declaring_no_test_yet_against_an_absent_item_is_an_error(
    tmp_path: Path,
) -> None:
    """An id the queue never held is a hole with a plausible-looking label."""
    root = _family_repo(tmp_path, "no test yet (`PL-ZZZZ`)", items={"PL-8888": "ready"})
    errors = _family_errors(root)

    assert len(errors) == 1
    assert "the queue does not hold" in errors[0]


def test_a_family_member_naming_nothing_at_all_is_an_error(tmp_path: Path) -> None:
    """The case the whole convention exists for: a `must` with no link.

    The sentence reads exactly as it did when something held it up, which is
    why nothing short of requiring the name catches it.
    """
    errors = _family_errors(_family_repo(tmp_path, "the interface is careful about it"))

    assert len(errors) == 1
    assert "names no test and does not declare that it has none" in errors[0]


def test_a_declared_absence_is_declined_rather_than_failed_without_a_store(tmp_path: Path) -> None:
    """A checkout with no queue has not disproved the forward reference."""
    root = _family_repo(tmp_path, "no test yet (`PL-8888`)")
    report = doc_check.analyze(root)

    assert _family_errors(root) == []
    assert any("no queue in this checkout can resolve" in d for d in report.declined)


def test_a_bound_family_whose_heading_has_moved_is_an_error(tmp_path: Path) -> None:
    """A renamed heading must not retire the family quietly.

    `BOUND_FAMILIES` still claims to hold it, so reading no members as "nothing
    to check" would be the same silent decay the check exists to catch, one
    level up from the row.
    """
    model = MODEL.replace("## Reasonably foreseeable misuse, and the", "## Misuse and the")
    errors = [e for e in _errors(_repo(tmp_path, model=model)) if "bound family" in e]

    assert len(errors) == 1
    assert "the heading has moved or its entries are gone" in errors[0]


LIST_FAMILY_DOCUMENT = "\n".join(
    [
        "## Minimum displayed outputs",
        "",
        "The interface must show:",
        "",
        "- simulated time;",
        "- the rate simulated time is advancing at, held by",
        "  `test_the_clock_states_its_playback_rate`;",
        "- run state; and",
        "  - a nested note, which is part of the entry above rather than one of its own",
        "- why a run halted, whenever one has.",
        "",
        "A closing paragraph, which is not a member.",
        "",
        "### What this list requires once the layout is the reader's",
        "",
        "- a bullet under a subsection, which belongs to that subsection",
        "",
    ]
)


def _list_family(
    heading: str = "Minimum displayed outputs", level: int = 2
) -> doc_check.BoundFamily:
    """A list-shaped family over `LIST_FAMILY_DOCUMENT`, built here rather than
    read from `BOUND_FAMILIES`.

    The shape is what these tests are about, so they must keep answering after
    the tuple's entries change - and they have to be able to ask about a
    heading the document does not carry, which no real entry can.
    """
    return doc_check.BoundFamily(
        document=doc_check.MODEL,
        heading=heading,
        level=level,
        kind=doc_check.TEST_ENTITY,
        members=doc_check._list_members,
        promise="every entry names the test that holds it",
    )


def test_a_list_shaped_family_reads_one_member_per_top_level_entry() -> None:
    """Wrapped entries and nested bullets fold into the entry they belong to.

    A member of this shape routinely wraps, so a walker reading one line at a
    time would see an entity named on a bullet's second line as named by
    nothing - which is the forgotten-link error this check exists to report,
    raised against a member that is conforming.
    """
    members = list(doc_check._list_members(LIST_FAMILY_DOCUMENT, _list_family()))

    assert [line for line, _ in members] == [5, 6, 8, 10]
    assert "`test_the_clock_states_its_playback_rate`" in members[1][1]
    assert "a nested note" in members[2][1]


def test_a_list_shaped_family_stops_at_the_next_subsection() -> None:
    """The bullets of a following subsection are that subsection's, not this
    family's.

    § "Minimum displayed outputs" is closed by a subsection that carries
    bullets of its own, so a family reading to the end of the section would
    hold prose about the list to the promise the list makes.
    """
    members = list(doc_check._list_members(LIST_FAMILY_DOCUMENT, _list_family()))

    assert all("under a subsection" not in member for _, member in members)


def test_a_list_shaped_family_whose_heading_has_moved_reads_no_members() -> None:
    """Which `check_bound_families` reports as an error rather than a pass.

    The walker's own answer is emptiness; the decision that emptiness is a
    failure is made once, for every shape, where the family is checked.
    """
    assert list(doc_check._list_members(LIST_FAMILY_DOCUMENT, _list_family("Moved"))) == []
    assert list(doc_check._list_members(LIST_FAMILY_DOCUMENT, _list_family(level=3))) == []


def test_this_repository_holds_every_bound_family_to_its_members() -> None:
    """The families named in `BOUND_FAMILIES` conform here, not only in fixtures.

    A family joins that tuple only once its annotation pass has landed, so this
    is the assertion that the tuple never runs ahead of the document.
    """
    report = doc_check.Report()
    doc_check.check_bound_families(Path(__file__).resolve().parents[2], report)

    assert report.errors == []
    assert report.declined == []


# --- the `not-delegable` subset count ----------------------------------------
#
# The three counts above state a list's *length*. This one states a property of
# its entries, and it is the only such count in the file that can be checked at
# all: `docket` reads `not-delegable:` off each item, so the number is a query
# over a field rather than a judgment about what an entry's work touches.
# `PL-GLBF` records why its two neighbours in the same section - "the two
# entries that change repository configuration" and "three entries reach into
# `src/`" - are left to the reader instead.

WITHHELD_GATE_ROADMAP = VERSIONED_GATE_ROADMAP.replace(
    "### Definition of done",
    "**Two entries are marked `not-delegable`,** which is worth knowing before\n"
    "the work is planned.\n\n### Definition of done",
)


def _withheld_errors(root: Path) -> list[str]:
    return [error for error in _errors(root) if "not-delegable" in error]


def _withheld_repo(tmp_path: Path, roadmap: str = WITHHELD_GATE_ROADMAP) -> Path:
    """A gate whose five entries hold two items withheld from delegation."""
    root = _repo(tmp_path, roadmap=roadmap)
    for identifier in ("PL-BBBB", "PL-CCCC", "PL-DDDD", "PL-FFFF", "PL-GGGG", "PL-HHHH"):
        _queue_item(root, identifier, classes="defect")
    _queue_item(root, "PL-BBBB", classes="defect", not_delegable="only a release proves it")
    _queue_item(root, "PL-DDDD", classes="defect", not_delegable="the setting is outside the tree")
    return root


def test_not_delegable_subset_count(tmp_path: Path) -> None:
    """A `not-delegable` count is held to the items, in both directions.

    The failure this closes is `PL-GLBF`'s: the sentence is hand-maintained, so
    it goes stale the next time an entry gains or loses the field, and until now
    nothing failed when it did.
    """
    root = _withheld_repo(tmp_path)

    assert _withheld_errors(root) == []

    stale = WITHHELD_GATE_ROADMAP.replace("**Two entries are marked", "**Four entries are marked")
    errors = _withheld_errors(_withheld_repo(tmp_path / "stale", roadmap=stale))

    assert len(errors) == 1
    assert "says 4 of v0.4.0's frozen entries" in errors[0]
    assert "but 2 of them hold an item carrying that field" in errors[0]


def test_a_not_delegable_count_counts_entries_rather_than_ids(tmp_path: Path) -> None:
    """One problem recorded under two ids is one entry, as everywhere else here.

    `PL-FFFF` and `PL-GGGG` share a line of the fixture's frozen list. Marking
    both leaves the count at three, not four - the same rule `GateEntry` states
    for the list's own size.
    """
    roadmap = WITHHELD_GATE_ROADMAP.replace("**Two entries are", "**Three entries are")
    root = _withheld_repo(tmp_path, roadmap=roadmap)
    for identifier in ("PL-FFFF", "PL-GGGG"):
        _queue_item(root, identifier, classes="defect", not_delegable="one problem, two ids")

    assert _withheld_errors(root) == []


def test_a_not_delegable_count_outside_the_gate_subsection_is_left_alone(tmp_path: Path) -> None:
    """Position fixes the meaning, so a sentence elsewhere counts nothing.

    A `Definition of done` bullet saying what a *later* milestone withholds is
    not a claim about this frozen list, and reading it as one would fail a
    correct sentence.
    """
    roadmap = WITHHELD_GATE_ROADMAP.replace(
        "- Everything above is done.",
        "- Everything above is done, and nine entries are marked `not-delegable` in v0.5.0.",
    )

    assert _withheld_errors(_withheld_repo(tmp_path, roadmap=roadmap)) == []


def test_a_not_delegable_count_is_declined_when_there_is_no_store(tmp_path: Path) -> None:
    """A store that is not there decides nothing, and says so rather than failing.

    `read_items` answers `[]` for an absent directory, which is right for the
    advisory that already reads it and would be a confident wrong answer here -
    every stated count would read as wrong by exactly its own size. A truncated
    checkout is the live case.
    """
    root = _withheld_repo(tmp_path)
    for item in (root / "docs" / "items").iterdir():
        item.unlink()
    (root / "docs" / "items").rmdir()

    report = doc_check.analyze(root)

    assert _withheld_errors(root) == []
    assert any("not-delegable" in line and "did not answer" in line for line in report.declined)


def test_a_not_delegable_count_is_declined_when_an_entry_id_has_no_item(tmp_path: Path) -> None:
    """A missing id makes the count uncomputable, not smaller.

    Read as "not withheld" it would fail a correct sentence and name the prose
    as the fault, on a tree whose real fault is the store. Nothing else in this
    file reports a frozen entry whose id has no item, so the decline is the
    only place that state is visible.
    """
    root = _withheld_repo(tmp_path)
    (root / "docs" / "items" / "PL-HHHH-demo.md").unlink()

    report = doc_check.analyze(root)

    assert _withheld_errors(root) == []
    assert any("not-delegable" in line and "did not answer" in line for line in report.declined)


# --- line citations ---------------------------------------------------------


def _items(root: Path, briefs: Mapping[str, str]) -> Path:
    """Write item briefs under `docs/items/`, keyed by the filename to write.

    A mapping rather than `**briefs`, because an id cannot be an identifier:
    the keyword form spelled it `PL_8888_open` and this helper put the hyphens
    back, which is the one spelling `tools/fixture_id_check.py` reads a rule
    of its own to see (`PL-L609`). Keyed this way the ids are ordinary string
    literals, which is the scan's main rule - and the closed-brief test below
    no longer needs `**{identifier: ...}` to pass an id that is not a name.
    """
    items = root / "docs" / "items"
    items.mkdir(parents=True, exist_ok=True)
    for name, body in briefs.items():
        (items / f"{name}.md").write_text(body, encoding="utf-8")
    return root


def _line_citation_errors(root: Path) -> list[str]:
    report = doc_check.Report()
    doc_check.check_line_citations(root, {}, report)
    return report.errors


def _brief(status: str, body: str) -> str:
    return f"id: PL-T3ST\nstatus: {status}\n\n**Problem.** {body}\n"


def test_a_line_citation_past_the_end_of_its_file_is_an_error(tmp_path: Path) -> None:
    """The one thing about a line citation that can be decided without judgment.

    Line 900 of a 1-line file cannot be what the sentence says, whatever the
    sentence says, so this is resolvability rather than truth - the same
    question `check_citations` asks of a path, one line finer.
    """
    root = _items(_repo(tmp_path), {"PL-8888-open": _brief("ready", "See `core/thing.py:900`.")})

    errors = _line_citation_errors(root)

    assert len(errors) == 1
    assert "core/thing.py:900" in errors[0]
    assert "has 0 lines" in errors[0]


def test_a_line_citation_inside_its_file_stays_quiet(tmp_path: Path) -> None:
    """Whether the line still holds the symbol is judgment, and is not decided here.

    A checker that fired on a citation it cannot evaluate would be disabled,
    which is the same as not having it.
    """
    root = _repo(tmp_path)
    (root / "src" / "anesthesia_sim" / "core" / "thing.py").write_text(
        "one\ntwo\nthree\n", encoding="utf-8"
    )
    _items(root, {"PL-8888-open": _brief("ready", "See `core/thing.py:2`.")})

    assert _line_citation_errors(root) == []


def test_a_closed_brief_is_exempt(tmp_path: Path) -> None:
    """`PL-G424`'s recorded decision, and the reason this check is worth having.

    A closed brief describes the tree as it was when the work was done. Holding
    one to today's tree would have raised 196 errors across this store that no
    session should act on - and a check nobody may act on trains a reader to
    skim the output where a real failure is printed.
    """
    root = _repo(tmp_path)
    # Spelled out rather than derived from the status, because `f"PL-{status.upper()}"`
    # mints `PL-DONE` and `PL-DROPPED`, neither of which is in `store.ID_ALPHABET`.
    for status, identifier in (("done", "PL-D0N3"), ("dropped", "PL-DRPD")):
        _items(root, {identifier: _brief(status, "See `core/thing.py:900`.")})

    assert _line_citation_errors(root) == []


def test_an_item_may_quote_the_broken_citation_it_reports(tmp_path: Path) -> None:
    """An item whose subject is a stale citation must be able to show it.

    Without the escape, reporting the defect *is* the defect, and the only way
    to file the finding is to write it wrong.
    """
    root = _items(
        _repo(tmp_path),
        {"PL-8888-open": _brief("ready", "It still says:\n\n```text\ncore/thing.py:900\n```\n")},
    )

    assert _line_citation_errors(root) == []


def test_an_ambiguous_bare_filename_declines(tmp_path: Path) -> None:
    """Two files of one name cannot say which line count the sentence meant.

    Picking either is a wrong answer stated confidently, which this tool holds
    to be worse than no answer.
    """
    root = _repo(tmp_path, modules=("core/thing.py", "app/thing.py"))
    _items(root, {"PL-8888-open": _brief("ready", "See `thing.py:900`.")})

    assert _line_citation_errors(root) == []


def test_this_repository_resolves_every_live_line_citation() -> None:
    # The rule against the real store rather than a fixture: this is the one
    # that catches the third generation of a hand-repaired line number.
    report = doc_check.Report()
    root = Path(__file__).resolve().parents[2]
    doc_check.check_line_citations(root, doc_check.read_docs(root), report)

    assert report.errors == []


def test_a_family_member_may_declare_no_test_yet_against_a_historical_id(tmp_path: Path) -> None:
    """The declared-none form took a four-character id only, so `PL-001` failed it.

    43 of the store's ids are three digits, and against one of them the fixed
    parenthesis `docs/MODEL.md` clause 3 prescribes read as no declaration at
    all - a hard error on a row that had done exactly what the clause asks
    (`PL-KYW3`).
    """
    root = _family_repo(tmp_path, "no test yet (`PL-001`)", items={"PL-001": "ready"})

    assert _family_errors(root) == []


# --- what a tag's span covers -----------------------------------------------


NOTES_0_2_4 = "## v0.2.4 - 2026-09-01\n\n### defect\n\n- PL-9WX1 The stamped one - #10\n"
NOTES_0_2_5 = "## v0.2.5 - 2026-09-08\n\n### defect\n\n- PL-7KD2 The late one - #11\n"


def _git_run(root: Path, *command: str) -> None:
    # Real git, for the reason `_git_init` gives: what is under test is how
    # doc_check reads a checkout, so a stub would test the stub.
    subprocess.run(("git", *command), cwd=root, check=True, capture_output=True)


def _closed(pr: str, milestone: str) -> str:
    return f"status: done\nclosed: 2026-09-07\nmilestone: {milestone}\npr: {pr}\n"


def _span_repo(
    tmp_path: Path,
    history: Sequence[tuple[str, Mapping[str, str], str]],
    items: Mapping[str, str],
    *,
    name: str = "spans",
) -> Path:
    """A checkout whose history carries release tags, notes files and a store.

    `history` is one entry per commit, oldest first: its subject, the files it
    writes, and the release tag to put on it or `""` for none. Written this way
    rather than as a fixed fixture because every rule below turns on *where* in
    a span a commit sits, which only a real ordering can express.
    """
    root = tmp_path / name
    (root / "docs" / "items").mkdir(parents=True, exist_ok=True)
    (root / "docs" / "releases").mkdir(parents=True, exist_ok=True)
    (root / "docket.toml").write_text('items_dir = "docs/items"\n', encoding="utf-8")
    for identifier, front in items.items():
        (root / "docs" / "items" / f"{identifier}-demo.md").write_text(
            f"---\nid: {identifier}\ntitle: Demo\npriority: P2\neffort: S\n{front}"
            "classes: docs\nadded: 2026-09-06\n---\n\n**Problem.** A thing.\n"
            "**Why it matters.** It does.\n**Done when.** Fixed.\n",
            encoding="utf-8",
        )
    _git_run(root, "init", "-q")
    _git_run(root, "config", "user.email", "test@example.invalid")
    _git_run(root, "config", "user.name", "Test")
    for subject, files, tag in history:
        for relative, text in files.items():
            written = root / relative
            written.parent.mkdir(parents=True, exist_ok=True)
            written.write_text(text, encoding="utf-8")
        _git_run(root, "add", "-A")
        _git_run(root, "commit", "-qm", subject)
        if tag:
            _git_run(root, "tag", tag)
    return root


#: The ordinary shape: v0.2.4 stamped `#10` and was cut in `#12`, while `#11`
#: merged before that cut without being stamped. v0.2.5 follows so that v0.2.4's
#: span is a closed one and therefore judged.
SPAN_HISTORY: tuple[tuple[str, dict[str, str], str], ...] = (
    ("PL-9WX1: the stamped one (#10)", {"work.txt": "a"}, ""),
    ("PL-7KD2: the late one (#11)", {"work.txt": "b"}, ""),
    ("PL-3NP4: cut v0.2.4 (#12)", {"docs/releases/v0.2.4.md": NOTES_0_2_4}, "v0.2.4"),
    ("PL-6RT5: cut v0.2.5 (#13)", {"docs/releases/v0.2.5.md": NOTES_0_2_5}, "v0.2.5"),
)

SPAN_ITEMS = {
    "PL-9WX1": _closed("10", "v0.2.4"),
    "PL-7KD2": _closed("11", "v0.2.5"),
    "PL-3NP4": _closed("12", "v0.2.5"),
    "PL-6RT5": "status: done\nclosed: 2026-09-14\npr: 13\n",
}


def _span_report(root: Path) -> doc_check.Report:
    report = doc_check.Report()
    doc_check.check_tag_span_covers_its_notes(root, report)
    return report


def test_a_closure_inside_a_span_its_notes_never_name_is_an_error(tmp_path: Path) -> None:
    """`PL-P669`: the two records disagree and neither points at the other.

    `#11` merged while v0.2.4 was being cut, so `git describe --contains`
    resolves it to v0.2.4 while v0.2.4's own notes stop short of it.
    """
    errors = _span_report(_span_repo(tmp_path, SPAN_HISTORY, SPAN_ITEMS)).errors

    assert len(errors) == 1
    assert errors[0].startswith("docs/releases/v0.2.4.md: 1 closing pull request")
    assert "(#11)" in errors[0]


def test_the_error_carries_the_line_that_clears_it(tmp_path: Path) -> None:
    """The message states the repair rather than the rule, so it can be pasted.

    `CLAUDE.md` asks a tool to print the few lines a decision needs instead of
    making the reader assemble them; here that is the bullet and the heading it
    belongs under, which is also what stops the line landing among what the cut
    stamped.
    """
    errors = _span_report(_span_repo(tmp_path, SPAN_HISTORY, SPAN_ITEMS)).errors

    assert doc_check.SPAN_HEADING in errors[0]
    assert "`- PL-7KD2 - #11 - described in v0.2.5`" in errors[0]


def test_naming_the_closure_in_the_notes_clears_it(tmp_path: Path) -> None:
    """The pointer is the whole requirement, and where it sits is the reader's.

    Both dispositions `PL-028F` left with a person satisfy this: a cut re-run
    that absorbs the work names it among the bullets, and a pointer section
    names it while leaving the cut's own account alone.
    """
    root = _span_repo(tmp_path, SPAN_HISTORY, SPAN_ITEMS)
    notes = root / "docs" / "releases" / "v0.2.4.md"
    notes.write_text(
        notes.read_text(encoding="utf-8")
        + f"\n{doc_check.SPAN_HEADING}\n\n"
        + doc_check.span_bullet(("PL-7KD2",), "11", "v0.2.5")
        + "\n",
        encoding="utf-8",
    )

    assert _span_report(root).errors == []


def test_a_span_whose_notes_name_every_closure_is_quiet(tmp_path: Path) -> None:
    """The common case, and the one that decides whether this check earns its place."""
    notes = NOTES_0_2_4 + "- PL-7KD2 The late one - #11\n"
    history = tuple(
        (subject, {"docs/releases/v0.2.4.md": notes}, tag)
        if tag == "v0.2.4"
        else (subject, files, tag)
        for subject, files, tag in SPAN_HISTORY
    )

    report = _span_report(_span_repo(tmp_path, history, SPAN_ITEMS))

    assert (report.errors, report.advisories, report.declined) == ([], [], [])


def test_a_releases_own_cut_is_not_a_closure_its_notes_owe_a_line(tmp_path: Path) -> None:
    """Inside its own span by construction, and stamped by the next release every time.

    `#12` cut v0.2.4 and `PL-3NP4` carries `milestone: v0.2.5`, which is the
    convention `ROADMAP.md` § "Tags" writes down. It accounted for 40 of the 63
    span-crossing closures in this repository on 2026-09-22, so reporting it
    would bury the 23 that are findings.
    """
    errors = _span_report(_span_repo(tmp_path, SPAN_HISTORY, SPAN_ITEMS)).errors

    assert not any("#12" in message for message in errors)


def test_the_cut_is_found_from_the_notes_it_added_not_from_its_subject(tmp_path: Path) -> None:
    """A release whose cut is worded another way keeps its exemption.

    "cut v0.2.4" is prose and nothing holds a subject to it; the commit that
    *added* `docs/releases/v0.2.4.md` is a fact about the tree.
    """
    history = tuple(
        ("PL-3NP4: ship it (#12)", files, tag) if tag == "v0.2.4" else (subject, files, tag)
        for subject, files, tag in SPAN_HISTORY
    )

    errors = _span_report(_span_repo(tmp_path, history, SPAN_ITEMS)).errors

    assert not any("#12" in message for message in errors)


def test_the_newest_spans_strangers_are_not_reported_yet(tmp_path: Path) -> None:
    """Its pointer would have to name a release that has not been cut.

    Requiring it would turn `make check` red on a state nobody can clear, which
    is the failure `PL-8HJ2` removed and the one `check_tags` stays silent on
    for the same reason. `#13` cut v0.2.5 and is stamped by nothing yet.
    """
    errors = _span_report(_span_repo(tmp_path, SPAN_HISTORY, SPAN_ITEMS)).errors

    assert not any("v0.2.5.md" in message for message in errors)


def test_a_dropped_items_pull_request_is_not_a_closure(tmp_path: Path) -> None:
    """Nothing shipped, so no release's notes owe it a line."""
    items = dict(SPAN_ITEMS)
    items["PL-7KD2"] = "status: dropped\nclosed: 2026-09-07\nreason: Superseded.\npr: 11\n"

    assert _span_report(_span_repo(tmp_path, SPAN_HISTORY, items)).errors == []


def test_a_closure_whose_subject_carries_no_number_is_invisible(tmp_path: Path) -> None:
    """A floor on what the span read can prove, not a rule about it.

    85 of this store's recorded pull requests are in that state, all numbered 3
    to 105, from before the squash-subject convention. Saying nothing is the
    honest answer: the commit cannot be placed in a span at all.
    """
    history = tuple(
        ("PL-7KD2: the late one", files, tag) if "#11" in subject else (subject, files, tag)
        for subject, files, tag in SPAN_HISTORY
    )

    assert _span_report(_span_repo(tmp_path, history, SPAN_ITEMS)).errors == []


def test_a_truncated_clone_declines_instead_of_reporting_a_span_it_cannot_walk(
    tmp_path: Path,
) -> None:
    """The shape `check_tags` settled on, withholding only what truncation invents.

    A shallow clone holds some tags and not the commits between them, so a span
    it cannot walk and one whose notes are genuinely short look identical from
    inside it.
    """
    origin = _span_repo(tmp_path, SPAN_HISTORY, SPAN_ITEMS, name="origin")
    clone = tmp_path / "shallow"
    subprocess.run(
        ("git", "clone", "-q", "--depth", "3", "--no-local", origin.as_uri(), str(clone)),
        check=True,
        capture_output=True,
    )

    report = _span_report(clone)

    assert report.errors == []
    assert any("shallow clone" in message for message in report.declined)


def test_a_store_that_will_not_read_declines(tmp_path: Path) -> None:
    """A check that never ran is never reported as one that passed (`PL-XCYB`)."""
    root = _span_repo(tmp_path, SPAN_HISTORY, SPAN_ITEMS)
    for brief in (root / "docs" / "items").glob("*.md"):
        brief.unlink()
    (root / "docs" / "items").rmdir()

    report = _span_report(root)

    assert report.errors == []
    assert any("item store would not read" in message for message in report.declined)


def test_one_pull_request_stamped_by_two_releases_gets_a_line_for_each(tmp_path: Path) -> None:
    """`#225` closed `PL-SZ56`, stamped by v0.3.0, and `PL-21GS`, stamped by v0.4.15.

    One bullet naming both releases would leave the reader to work out which id
    is described where, which is the lookup the pointer exists to remove.
    """
    items = dict(SPAN_ITEMS)
    items["PL-9WX1"] = _closed("11", "v0.3.0")
    notes = NOTES_0_2_4.replace("- PL-9WX1 The stamped one - #10\n", "")
    history = tuple(
        (subject, {"docs/releases/v0.2.4.md": notes}, tag)
        if tag == "v0.2.4"
        else (subject, files, tag)
        for subject, files, tag in SPAN_HISTORY
    )

    errors = _span_report(_span_repo(tmp_path, history, items)).errors

    assert len(errors) == 1
    assert "`- PL-7KD2 - #11 - described in v0.2.5`" in errors[0]
    assert "`- PL-9WX1 - #11 - described in v0.3.0`" in errors[0]


def test_a_repository_that_writes_no_release_notes_is_told_nothing(tmp_path: Path) -> None:
    """Silence rather than a decline, the shape `release.is_untagged` uses.

    Adopting the practice is the project's decision and not this tool's, so a
    checkout that keeps no notes is told nothing at all. A decline there would
    report an unrun check on every run of every such checkout, which costs
    attention forever and changes no decision.
    """
    root = _span_repo(tmp_path, SPAN_HISTORY, SPAN_ITEMS, name="bare")
    for notes in (root / "docs" / "releases").glob("*.md"):
        notes.unlink()
    (root / "docs" / "releases").rmdir()

    report = _span_report(root)

    assert (report.errors, report.declined) == ([], [])
