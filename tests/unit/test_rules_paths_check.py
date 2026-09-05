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


def _rules(tmp_path: Path, **files: str) -> Path:
    """A repository root holding `.claude/rules/<name>.md` for each keyword."""
    rules = tmp_path / rules_paths_check.RULES_DIR
    rules.mkdir(parents=True)
    for name, body in files.items():
        (rules / f"{name}.md").write_text(body, encoding="utf-8")
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
    root = _rules(tmp_path, freeze=_frontmatter("/README.md", "/src/**"))

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
        tmp_path, freeze='---\npaths:\n  - "/README.md"\nname: not-a-glob\n---\n\n# A rule\n'
    )

    assert rules_paths_check.problems(root) == []


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


def test_this_repository_passes_its_own_check() -> None:
    """The real tree, not only a fixture: the rule has to hold where it is enforced."""
    assert rules_paths_check.problems(ROOT) == []
