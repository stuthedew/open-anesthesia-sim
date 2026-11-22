"""Tests for `tools/rules_paths_check.py`, the rule-scope anchoring guard.

The check exists because a `paths:` entry fails silently in both directions.
Unanchored, it also matches its name at any depth, which put the README freeze
on `subprojects/docket/README.md` - the queue tool's manual - alongside a rule
whose own text says every sentence of it is wrong when applied to a `README.md`
(`PL-ZQ35`). Spelled `./`, it matches nothing at all, so the rule is never
delivered and nothing says so.

The interesting tests are therefore not the happy path. They are the two
silences: the entry that is too wide, and the entry that reaches nowhere, each
asserted to produce a message naming the replacement rather than only the
offence - a failure that says "this is wrong" without saying what to write
sends the reader back to the measurement.

The rest guard the parser against reading scope it was not given: a resident
file with no frontmatter owes nothing, a key following the list is not an item
of it, and a block that never closes is reported rather than skipped, because
skipping it would pass a file whose declared scope could not be read at all.
"""

from __future__ import annotations

from pathlib import Path

import pytest
import rules_paths_check

ROOT = Path(rules_paths_check.__file__).resolve().parent.parent


def _rules(tmp_path: Path, *, tree: tuple[str, ...] = (), **files: str) -> Path:
    """A repository root holding `.claude/rules/<name>.md` for each keyword.

    `tree` is what the rules point *at* - a trailing slash makes a directory,
    anything else a file. An anchored entry is only correct if its target is
    really there, so a fixture testing the anchoring rule has to build one.
    """
    rules = tmp_path / rules_paths_check.RULES_DIR
    rules.mkdir(parents=True)
    for name, body in files.items():
        (rules / f"{name}.md").write_text(body, encoding="utf-8")
    for entry in tree:
        target = tmp_path / entry.rstrip("/")
        if entry.endswith("/"):
            target.mkdir(parents=True, exist_ok=True)
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text("", encoding="utf-8")
    return tmp_path


def _frontmatter(*globs: str) -> str:
    items = "".join(f'  - "{glob}"\n' for glob in globs)
    return f"---\npaths:\n{items}---\n\n# A rule\n"


def test_an_unanchored_entry_is_refused(tmp_path: Path) -> None:
    """The incident shape: `README.md` reached three files of that name."""
    root = _rules(tmp_path, freeze=_frontmatter("README.md"))

    found = rules_paths_check.problems(root)

    assert len(found) == 1
    assert "any depth" in found[0]
    assert '"/README.md"' in found[0]


def test_an_anchored_entry_is_accepted(tmp_path: Path) -> None:
    """A guard that fires on correct work gets worked around."""
    root = _rules(
        tmp_path, tree=("README.md", "src/"), freeze=_frontmatter("/README.md", "/src/**")
    )

    assert rules_paths_check.problems(root) == []


def test_the_dead_prefix_is_named_as_matching_nothing(tmp_path: Path) -> None:
    """`./` is the plausible keystroke that silently disables a rule."""
    root = _rules(tmp_path, freeze=_frontmatter("./README.md"))

    found = rules_paths_check.problems(root)

    assert len(found) == 1
    assert "matches nothing at all" in found[0]
    assert '"/README.md"' in found[0]


def test_an_inline_single_glob_is_read(tmp_path: Path) -> None:
    """The harness accepts a bare scalar after the key as well as a list."""
    root = _rules(tmp_path, freeze='---\npaths: "docs/MODEL.md"\n---\n\n# A rule\n')

    found = rules_paths_check.problems(root)

    assert len(found) == 1
    assert '"/docs/MODEL.md"' in found[0]


def test_a_file_with_no_frontmatter_owes_nothing(tmp_path: Path) -> None:
    """A resident rule declares no scope, which is a legitimate shape here."""
    root = _rules(tmp_path, resident="# Always loaded\n\nsrc/** is only prose here.\n")

    assert rules_paths_check.problems(root) == []


def test_a_later_key_is_not_read_as_a_path(tmp_path: Path) -> None:
    """The list ends at the first line that is not one of its items."""
    root = _rules(
        tmp_path,
        tree=("README.md",),
        freeze='---\npaths:\n  - "/README.md"\nname: not-a-glob\n---\n\n# A rule\n',
    )

    assert rules_paths_check.problems(root) == []


@pytest.mark.parametrize(
    ("first", "second"),
    [
        ('    - "/src/**"', '  - "/README.md"'),
        ('  - "/src/**"', '- "/README.md"'),
        ('  - "/src/**"', '\t- "/README.md"'),
    ],
    ids=["shallower", "at the key's column", "after a tab"],
)
def test_an_item_off_the_list_s_indentation_is_refused_by_name(
    tmp_path: Path, first: str, second: str
) -> None:
    """YAML refuses the front matter, so neither glob is the rule's scope (`PL-PPNV`).

    Read as two globs, both resolving, the check passed a rule whose scope
    YAML reads as nothing.
    """
    root = _rules(
        tmp_path,
        tree=("src/", "README.md"),
        rule=f"---\npaths:\n{first}\n{second}\n---\n\n# A rule\n",
    )

    assert rules_paths_check.problems(root) == [
        f".claude/rules/rule.md: `{second.strip()}` under `paths:` is not at the list's "
        "indentation, or a tab indents it, which YAML refuses; write each glob as a `- ` item "
        "at the list's indentation, so the scope it declares was not read"
    ]


def test_an_unterminated_block_is_reported_rather_than_skipped(tmp_path: Path) -> None:
    """Declared scope that cannot be read is the failure, not an absence of one."""
    root = _rules(tmp_path, broken='---\npaths:\n  - "/README.md"\n\n# No closing rule\n')

    found = rules_paths_check.problems(root)

    assert len(found) == 1
    assert "never closed" in found[0]


def test_every_offender_is_named_not_only_the_first(tmp_path: Path) -> None:
    """One run has to clear the tree; a check reporting one at a time costs a cycle each."""
    root = _rules(
        tmp_path, one=_frontmatter("tools/**", "docs/worker.md"), two=_frontmatter("src/**")
    )

    assert len(rules_paths_check.problems(root)) == 3


def test_the_failure_prints_to_stderr_and_exits_one(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root = _rules(tmp_path, freeze=_frontmatter("README.md"))
    monkeypatch.setattr("sys.argv", ["rules_paths_check.py", "--root", str(root)])

    assert rules_paths_check.main() == 1

    captured = capsys.readouterr()
    assert captured.out == ""
    assert "README.md" in captured.err


def test_a_prefix_that_resolves_to_nothing_is_refused(tmp_path: Path) -> None:
    """Anchored and dead: it passes the first rule and delivers to nobody."""
    root = _rules(tmp_path, freeze=_frontmatter("/scr/anesthesia_sim/core/**"))

    found = rules_paths_check.problems(root)

    assert len(found) == 1
    assert "points at nothing" in found[0]


def test_the_message_names_where_the_path_stopped_being_real(tmp_path: Path) -> None:
    """A transposed segment reads as correct; the nearest ancestor is what shows the typo."""
    root = _rules(
        tmp_path, tree=("src/anesthesia_sim/",), freeze=_frontmatter("/src/anesthesia_sim/nope/**")
    )

    found = rules_paths_check.problems(root)

    assert len(found) == 1
    assert 'Nearest existing path: "src/anesthesia_sim"' in found[0]


def test_a_pattern_below_a_file_is_refused(tmp_path: Path) -> None:
    """`/README.md/**` resolves, and still matches nothing."""
    root = _rules(tmp_path, tree=("README.md",), freeze=_frontmatter("/README.md/**"))

    found = rules_paths_check.problems(root)

    assert len(found) == 1
    assert "a file rather than a directory" in found[0]


def test_a_pattern_rooted_at_the_repository_is_accepted(tmp_path: Path) -> None:
    """`/**` has no literal prefix, and the root is always there."""
    root = _rules(tmp_path, freeze=_frontmatter("/**"))

    assert rules_paths_check.problems(root) == []


def test_a_pattern_beginning_mid_segment_is_judged_on_its_directory(tmp_path: Path) -> None:
    """`/src/foo*.md` asserts `src/` exists and says nothing about `foo`."""
    root = _rules(tmp_path, tree=("src/",), freeze=_frontmatter("/src/foo*.md"))

    assert rules_paths_check.problems(root) == []


def test_a_rule_in_a_subdirectory_is_read(tmp_path: Path) -> None:
    """`PL-9NZ3`: Claude Code discovers `.claude/rules/` recursively, so a nested rule loads.

    The top-level glob never read one, while `doc_check` measured it as a
    rule, so its `paths:` were held to nothing.
    """
    root = _rules(tmp_path)
    nested = root / rules_paths_check.RULES_DIR / "sub"
    nested.mkdir()
    (nested / "freeze.md").write_text(_frontmatter("README.md"), encoding="utf-8")

    (found,) = rules_paths_check.problems(root)

    assert found.startswith(".claude/rules/sub/freeze.md:")
    assert "any depth" in found


def test_this_repository_passes_its_own_check() -> None:
    """The real tree, not only a fixture: the rule has to hold where it is enforced."""
    assert rules_paths_check.problems(ROOT) == []


def test_a_doubled_single_quote_reads_as_docket_reads_it() -> None:
    """`'it''s'` kept both quotes here, and `"a\\"b"` its backslash (`PL-8MHZ`).

    `docket.frontmatter.unquote` is the one reading of a quoted scalar.
    """
    assert rules_paths_check.entries(["paths:", "  - '/it''s/**'", '  - "/a\\"b/**"']) == [
        "/it's/**",
        '/a"b/**',
    ]


@pytest.mark.parametrize(
    ("item", "why"),
    [
        ('  - "/src/**" extra', "holds `extra` after its closing quote"),
        ('  - "/src/\\q"', "a quoted glob YAML refuses"),
        ("  -", "holds no glob"),
    ],
)
def test_a_glob_yaml_refuses_or_one_holding_nothing_is_unreadable(item: str, why: str) -> None:
    """A tail after the quote was read into the glob, and a bare `-` named as no item."""
    with pytest.raises(rules_paths_check.Unreadable, match=why):
        rules_paths_check.entries(["paths:", item])


def _apparatus(
    tmp_path: Path,
    *,
    globs: tuple[str, ...] = ("/docs/worker.md", "/tools/**"),
    workflow: tuple[str, ...] = ("tools", "docs/worker.md", "Makefile", "tests/unit/test_x.py"),
    rest: str = "\n# The bar\n\nBody text.\n",
) -> Path:
    """A root holding the apparatus rule, a `docket.toml` and the paths it names."""
    rules = tmp_path / ".claude" / "rules"
    rules.mkdir(parents=True)
    items = "".join(f'  - "{glob}"\n' for glob in globs)
    (rules / "apparatus-standard.md").write_text(
        f"---\npaths:\n{items}---\n{rest}", encoding="utf-8"
    )
    listed = "".join(f'  "{entry}",\n' for entry in workflow)
    (tmp_path / "docket.toml").write_text(
        f"[docket]\nworkflow_paths = [\n{listed}]\n", encoding="utf-8"
    )
    (tmp_path / "tools").mkdir()
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "worker.md").write_text("", encoding="utf-8")
    return tmp_path


@pytest.fixture
def lane_only(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(rules_paths_check, "LANE_ONLY", ("Makefile",))


@pytest.mark.usefixtures("lane_only")
def test_a_paths_list_that_workflow_paths_gives_passes(tmp_path: Path) -> None:
    """Tests and `LANE_ONLY` entries are left out, directories take `/**`."""
    assert rules_paths_check.apparatus_set_problems(_apparatus(tmp_path)) == []


@pytest.mark.usefixtures("lane_only")
def test_a_path_added_to_workflow_paths_alone_is_refused_until_written(tmp_path: Path) -> None:
    """The refusal `PL-LY24` counted six times now names the command that ends it."""
    root = _apparatus(tmp_path, workflow=("tools", "docs/worker.md", "Makefile", "bin"))
    (root / "bin").mkdir()

    found = rules_paths_check.apparatus_set_problems(root)

    assert len(found) == 1
    assert "it lacks /bin/**" in found[0]
    assert "python3 tools/rules_paths_check.py --write" in found[0]


@pytest.mark.usefixtures("lane_only")
def test_write_adds_the_new_path_and_keeps_the_rest_of_the_rule(tmp_path: Path) -> None:
    """One edit to `workflow_paths` is the whole change: `--write` does the second."""
    root = _apparatus(
        tmp_path,
        workflow=("tools", "docs/worker.md", "Makefile", "bin"),
        rest="\n# The bar\n\npaths: in prose is not a key.\n",
    )
    (root / "bin").mkdir()

    added, removed = rules_paths_check.write_apparatus_paths(root)

    assert (added, removed) == (["/bin/**"], [])
    text = (root / rules_paths_check.APPARATUS_RULE).read_text(encoding="utf-8")
    assert text == (
        '---\npaths:\n  - "/bin/**"\n  - "/docs/worker.md"\n  - "/tools/**"\n---\n'
        "\n# The bar\n\npaths: in prose is not a key.\n"
    )
    assert rules_paths_check.apparatus_set_problems(root) == []
    assert rules_paths_check.write_apparatus_paths(root) == ([], [])


@pytest.mark.usefixtures("lane_only")
def test_a_glob_written_by_hand_is_refused_and_write_removes_it(tmp_path: Path) -> None:
    """A path added to the rule alone loads the standard on files no lane assigns it."""
    root = _apparatus(tmp_path, globs=("/docs/worker.md", "/src/**", "/tools/**"))

    found = rules_paths_check.apparatus_set_problems(root)
    assert len(found) == 1
    assert "it also names /src/**" in found[0]

    assert rules_paths_check.write_apparatus_paths(root) == ([], ["/src/**"])
    assert rules_paths_check.apparatus_set_problems(root) == []


@pytest.mark.usefixtures("lane_only")
def test_a_lane_only_path_is_not_written(tmp_path: Path) -> None:
    """`Makefile` is in the lane, and `LANE_ONLY` keeps the standard off it."""
    root = _apparatus(tmp_path)
    assert "/Makefile" not in rules_paths_check.apparatus_globs(root)


def test_a_stale_lane_only_entry_is_named(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(rules_paths_check, "LANE_ONLY", ("Makefile", "gone.md"))

    found = rules_paths_check.apparatus_set_problems(_apparatus(tmp_path))

    assert found == ["apparatus set: LANE_ONLY's gone.md is no longer in workflow_paths; drop it"]


@pytest.mark.usefixtures("lane_only")
def test_a_rule_with_no_paths_key_says_it_was_not_read(tmp_path: Path) -> None:
    """A list the check cannot find is reported, never read as empty or skipped."""
    root = _apparatus(tmp_path)
    (root / rules_paths_check.APPARATUS_RULE).write_text("# no frontmatter\n", encoding="utf-8")

    found = rules_paths_check.apparatus_set_problems(root)

    assert len(found) == 1
    assert "`paths:` was not read" in found[0]
    with pytest.raises(rules_paths_check.Unreadable):
        rules_paths_check.write_apparatus_paths(root)


@pytest.mark.usefixtures("lane_only")
def test_main_with_write_names_what_it_added(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = _apparatus(tmp_path, workflow=("tools", "docs/worker.md", "Makefile", "bin"))
    (root / "bin").mkdir()

    assert rules_paths_check.main(["--root", str(root)]) == 1
    assert rules_paths_check.main(["--root", str(root), "--write"]) == 0
    out = capsys.readouterr().out
    assert 'now loads on "/bin/**"' in out
    assert "add it to LANE_ONLY" in out


def test_this_repository_s_apparatus_set_agrees() -> None:
    assert rules_paths_check.apparatus_set_problems(ROOT) == []
