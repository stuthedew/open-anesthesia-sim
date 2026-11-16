"""`tools/new_prose.py --compare` must set each changed passage beside its old text.

Close-out step 8 runs the comparison to find a fact that an edit dropped and a
passage that grew. These tests pin which files the reader table in
`.claude/rules/plain-writing.md` names, which paragraphs, table rows,
docstrings, comments and string literals count as prose, how changed rows are
grouped into passages, and which facts are reported as gone.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import new_prose
import pytest
from docket.config import load
from new_prose import ROOT, RULE, document_units, main, prose_units, reader_table, readers_of

#: The number of words in `LONG`, which only has to be longer than `SHORT`. The
#: comparison reads units of any length, so it treats the two alike.
MIN_WORDS = 30
LONG = " ".join(["word"] * MIN_WORDS)
SHORT = "Two words."

SOURCE = f'''\
"""{LONG}"""

LIMIT = 3


def step(x):
    """{LONG}"""
    return x * LIMIT


def other(y):
    """{SHORT}"""
    # {LONG}
    return y
'''


def _git(cwd: Path, *args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=cwd, check=True, capture_output=True, text=True
    ).stdout


def _write(root: Path, path: str, text: str) -> None:
    (root / path).parent.mkdir(parents=True, exist_ok=True)
    (root / path).write_text(text, encoding="utf-8")


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    """A repository with `SOURCE` committed on `main`, and a branch `work` checked out."""
    _git(tmp_path, "init", "-q", "-b", "main")
    for key, value in (("user.email", "t@example.com"), ("user.name", "T")):
        _git(tmp_path, "config", key, value)
    _write(tmp_path, "src/pkg/model.py", SOURCE)
    _git(tmp_path, "add", "-A")
    _git(tmp_path, "commit", "-qm", "seed")
    _git(tmp_path, "checkout", "-qb", "work")
    return tmp_path


def test_prose_units_reads_docstrings_and_joined_comment_runs() -> None:
    source = 'def f():\n    """One line."""\n    # first\n    # second\n    return 1  # after\n'

    found = prose_units("src/f.py", source)

    assert [(unit.kind, unit.first, unit.last, unit.text) for unit in found] == [
        ("docstring", 2, 2, "One line."),
        ("comment", 3, 4, "first\nsecond"),
        ("comment", 5, 5, "after"),
    ]


def _commit(repo: Path, message: str) -> str:
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "--allow-empty", "-m", message)
    return _git(repo, "rev-parse", "HEAD").strip()


DOCUMENT = f"""\
# Model

{LONG}

- {LONG}

{SHORT}

```text
{LONG}
```

<!-- {LONG} -->

| Hazard | Mitigation |
| --- | --- |
| short | {LONG} |
"""


def test_document_units_reads_paragraphs_list_paragraphs_and_table_rows() -> None:
    """A heading, a fence and an HTML comment hold no prose, and a table row does."""
    found = document_units("docs/MODEL.md", DOCUMENT)

    assert [(unit.kind, unit.first, unit.last) for unit in found] == [
        ("paragraph", 3, 3),
        ("paragraph", 5, 5),
        ("paragraph", 7, 7),
        ("table row", 15, 15),
        ("table row", 17, 17),
    ]
    assert found[1].text == f"- {LONG}"
    assert found[4].text == f"| short | {LONG} |"


#: A reader table in the rule's form, with rows written for these tests alone.
READERS = """\
Some prose before the table.

| Kind of text | Reader | What they know | What they do not know | What they will do with it |
| --- | --- | --- | --- | --- |
| `docs/MODEL.md` | A clinician | Anesthesia. | Code. | Trust a value. |
| `docs/MODEL.md` | A forker | Python. | Our names. | Change a value. |
| Code in `src/` | A developer | Python. | Our history. | Change the code. |
| Replies to the owner | The owner | Anesthesia. | Tool names. | Decide. |
"""


def test_reader_table_reads_each_row_and_the_files_it_names() -> None:
    table = reader_table(READERS)

    assert [(reader.paths, reader.who, reader.will_do) for reader in table] == [
        (("docs/MODEL.md",), "A clinician", "Trust a value."),
        (("docs/MODEL.md",), "A forker", "Change a value."),
        (("src/",), "A developer", "Change the code."),
        ((), "The owner", "Decide."),
    ]


def test_a_row_naming_a_directory_names_every_file_under_it() -> None:
    table = reader_table(READERS)

    assert [reader.who for reader in readers_of(table, "src/pkg/model.py")] == ["A developer"]
    assert [reader.who for reader in readers_of(table, "docs/MODEL.md")] == [
        "A clinician",
        "A forker",
    ]
    assert readers_of(table, "srcx/model.py") == []
    assert readers_of(table, "README.md") == []


def test_a_rule_without_the_reader_table_is_refused() -> None:
    with pytest.raises(ValueError, match="no table headed"):
        reader_table("| Kind | Reader |\n| --- | --- |\n| `a` | b |\n")


@pytest.mark.parametrize(
    "path",
    [
        "src/anesthesia_sim/core/patient.py",
        "tests/unit/test_patient.py",
        "docs/MODEL.md",
        "README.md",
    ],
)
def test_the_rule_names_a_reader_for_every_kind_of_file_the_comparison_reads(path: str) -> None:
    """A rule edit that drops a row would leave that kind of file out of every comparison."""
    assert readers_of(new_prose.rule_table(), path)


@pytest.mark.parametrize(
    "path",
    [
        "docs/items/PL-22T5-close-out-s-prose-review-reads-only-the.md",
        ".claude/rules/plain-writing.md",
        ".claude/skills/docket/modes/close-out.md",
        "tools/new_prose.py",
        "subprojects/docket/src/docket/arming.py",
        "CLAUDE.md",
    ],
)
def test_the_comparison_leaves_out_the_workflow_files_and_item_briefs(path: str) -> None:
    """The project owner took these files out of the prose review on 2026-11-10.

    The writing rule still names a reader for each, so it applies to them.
    """
    assert readers_of(new_prose.whole_rule_table(), path)
    assert not readers_of(new_prose.rule_table(), path)


def test_each_unedited_reader_is_a_reader_the_rule_names() -> None:
    """A reworded "Reader" cell would otherwise bring its texts back into the comparison."""
    named = {reader.who for reader in new_prose.whole_rule_table()}
    assert set(new_prose.UNEDITED_READERS) <= named


#: The product document that the reader table leaves out on purpose. The rule's
#: paragraph under the table gives the reason: `bin/docket release` writes each
#: note from item titles.
UNREVIEWED_PRODUCT_DOCUMENTS = ("docs/releases",)


def test_every_product_document_has_a_reader_except_the_release_notes() -> None:
    """A product document added without a row would be left out of the comparison."""
    table = reader_table(RULE.read_text(encoding="utf-8"))
    unread = []
    for entry in load(ROOT).product_paths:
        if entry in UNREVIEWED_PRODUCT_DOCUMENTS:
            continue
        path = ROOT / entry
        documents = sorted(path.rglob("*.md")) if path.is_dir() else [path]
        for document in documents:
            relative = document.relative_to(ROOT).as_posix()
            if document.suffix == ".md" and not readers_of(table, relative):
                unread.append(relative)
    assert unread == []


def test_no_row_names_the_release_notes() -> None:
    """A release note is written from item titles, so no reader row names it."""
    table = reader_table(RULE.read_text(encoding="utf-8"))
    assert not readers_of(table, "docs/releases/v0.6.14.md")


#: A document whose first section holds a value, for the `--compare` tests.
PRECISION = """\
# Model

## Displayed precision

The MAC readout steps by 0.01 for every agent.

The percent readout is unchanged here.

The chart keeps its own scale.

## Next

Other text.
"""


def _compare(repo: Path, capsys: pytest.CaptureFixture[str]) -> str:
    assert main(["--root", str(repo), "--base", "main", "--compare"]) == 0
    return capsys.readouterr().out


@pytest.fixture
def precise(repo: Path) -> Path:
    """`repo` with `PRECISION` committed as `docs/MODEL.md` on `main`, and `work` checked out."""
    _git(repo, "checkout", "-q", "main")
    _write(repo, "docs/MODEL.md", PRECISION)
    _commit(repo, "add the model document")
    _git(repo, "checkout", "-q", "work")
    _git(repo, "merge", "-q", "main")
    return repo


def test_a_passage_that_grew_and_lost_a_number_is_reported(
    precise: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """The growth and the lost value are both named, against the paragraph they replaced.

    On `PL-ZDZ0` a passage grew from 163 words to about 210 and no review said
    so, and a trial rewrite dropped a value from a condition (`PL-J1ZM`).
    """
    grown = PRECISION.replace(
        "The MAC readout steps by 0.01 for every agent.",
        "The MAC readout steps by one hundredth of MAC for every agent, so that its\n"
        "last digit is worth the same amount whatever the agent.",
    )
    (precise / "docs/MODEL.md").write_text(grown, encoding="utf-8")

    out = _compare(precise, capsys)

    assert (
        'docs/MODEL.md § "Displayed precision", rows 5-6: 9 words on main, 25 now, 16 more' in out
    )
    assert "gone  0.01  (fork line 5: The MAC readout steps by 0.01 for every agent.)" in out


def test_hunks_parted_by_a_blank_line_are_one_passage_and_by_a_paragraph_two(
    precise: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Edits to two paragraphs side by side are one passage; a paragraph left alone parts them."""
    model = precise / "docs/MODEL.md"
    first = PRECISION.replace("for every agent.", "for each agent.")
    model.write_text(first.replace("unchanged here.", "the same here."), encoding="utf-8")

    out = _compare(precise, capsys)

    assert "1 passages of the reviewed files changed their prose" in out
    assert "rows 5-7: 15 words on main, 16 now, 1 more" in out

    model.write_text(first.replace("its own scale.", "a scale of its own."), encoding="utf-8")

    out = _compare(precise, capsys)

    assert "rows 5-5: 9 words on main, 9 now, the same count" in out
    assert "rows 9-9: 6 words on main, 8 now, 2 more" in out
    assert "These files hold every fact they held on main, as often." in out


def test_a_reflowed_paragraph_is_not_a_changed_passage(
    precise: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    reflowed = PRECISION.replace(
        "The MAC readout steps by 0.01 for every agent.",
        "The MAC readout steps by 0.01\nfor every agent.",
    )
    (precise / "docs/MODEL.md").write_text(reflowed, encoding="utf-8")

    assert "No passage of the reviewed files changed its prose" in _compare(precise, capsys)


def test_a_removed_paragraph_is_named_with_its_words_on_the_base(
    precise: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    removed = PRECISION.replace("The MAC readout steps by 0.01 for every agent.\n\n", "")
    (precise / "docs/MODEL.md").write_text(removed, encoding="utf-8")

    out = _compare(precise, capsys)

    assert 'docs/MODEL.md § "Displayed precision", rows 5-5 on main: removed, 9 words' in out
    assert "gone  0.01" in out


def test_a_section_split_under_new_subheadings_is_compared_whole(
    precise: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Text moved between new subheadings is counted against its whole section.

    When a rewrite added subheadings (`PL-J37P`), the first appeared to grow
    from 854 words to 1,050, and the next to shrink from 2,093 to 1,561
    (`PL-TTBF`). Here the first paragraph takes words from the third. An
    unchanged paragraph between them would otherwise split them into two
    passages, one under each new subheading.
    """
    split = PRECISION.replace(
        "The MAC readout steps by 0.01 for every agent.\n",
        "### Readouts\n\n"
        "The MAC readout steps by 0.01 for every agent, and the chart keeps its own scale.\n",
    ).replace("The chart keeps its own scale.\n", "### Chart\n\nThe chart is plain.\n")
    (precise / "docs/MODEL.md").write_text(split, encoding="utf-8")

    out = _compare(precise, capsys)

    assert "1 passages of the reviewed files changed their prose" in out
    assert (
        'docs/MODEL.md § "Displayed precision", rows 7-13: 15 words on main, 20 now, 5 more' in out
    )
    assert '§ "Readouts"' not in out
    assert '§ "Chart"' not in out


def test_passages_under_headings_new_all_the_way_up_are_compared_as_one_file(
    precise: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """When no heading appears on both sides, the file is their shared section.

    A single such passage keeps its own heading, because no text can have moved
    between it and another passage.
    """
    model = precise / "docs/MODEL.md"
    renamed = PRECISION.replace("# Model\n", "# The model\n").replace(
        "## Displayed precision", "## Precision on screen"
    )
    model.write_text(renamed.replace("its own scale.", "a scale of its own."), encoding="utf-8")

    assert '§ "Precision on screen", rows 9-9: 6 words on main, 8 now, 2 more' in _compare(
        precise, capsys
    )

    model.write_text(
        renamed.replace("for every agent.", "for each agent.").replace(
            "its own scale.", "a scale of its own."
        ),
        encoding="utf-8",
    )

    out = _compare(precise, capsys)

    assert "1 passages of the reviewed files changed their prose" in out
    assert "docs/MODEL.md, rows 5-9: 15 words on main, 17 now, 2 more" in out


def test_a_python_file_is_compared_by_its_prose_alone(
    repo: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """A code span the docstring lost is named on its row, and a number in code is not a fact."""
    _git(repo, "checkout", "-q", "main")
    _write(repo, "src/pkg/limits.py", 'def cap(x):\n    """Clip `x` at `LIMIT`."""\n    return 7\n')
    _commit(repo, "a docstring and a number in code")
    _git(repo, "checkout", "-q", "work")
    _git(repo, "merge", "-q", "main")
    _write(
        repo, "src/pkg/limits.py", 'def cap(x):\n    """Clip `x` at the limit."""\n    return 8\n'
    )

    out = _compare(repo, capsys)

    assert "src/pkg/limits.py, rows 2-2: 4 words on main, 5 now, 1 more" in out
    assert "gone  LIMIT  (fork line 2: Clip `x` at `LIMIT`.)" in out
    assert "gone  7" not in out


#: A reader table with a row for string literals in an interface package, for
#: the string-unit tests (`PL-Q98K`).
STRING_READERS = READERS.replace(
    "| Replies to the owner |",
    "| String literals in `src/pkg/app/` | A learner | Anesthesia. | Code. | Act on a notice. |\n"
    "| Replies to the owner |",
)

#: An interface module with a long docstring and a long notice beside it.
NOTICE = f'''\
def notice(level):
    """{LONG}"""
    return f"{LONG} at {{level}}"
'''


def test_string_units_reads_every_literal_but_docstrings_and_f_string_pieces() -> None:
    source = (
        'def f(x):\n    """Docstring."""\n    a = "one" "two"\n'
        '    return f"value {x:.2f} here", "three"\n'
    )

    found = new_prose.string_units("src/f.py", source)

    assert [(unit.kind, unit.first, unit.text) for unit in found] == [
        ("string", 3, "onetwo"),
        ("string", 4, "value {x} here"),
        ("string", 4, "three"),
    ]


def test_a_refusal_that_loses_its_value_is_reported(
    repo: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """An edit that drops the number a refusal names is caught by the comparison."""
    rule = repo / ".git" / "rule.md"
    rule.write_text(STRING_READERS, encoding="utf-8")
    monkeypatch.setattr(new_prose, "RULE", rule)
    refusal = 'def check(x):\n    raise ValueError("the flow must be at least 0.2 L/min")\n'
    _write(repo, "src/pkg/app/check.py", refusal)
    _git(repo, "add", "-A")
    _git(repo, "commit", "-qm", "refusal")
    _git(repo, "branch", "-f", "main")
    _write(repo, "src/pkg/app/check.py", refusal.replace("at least 0.2 L/min", "too low"))

    assert main(["--root", str(repo), "--base", "main", "--compare"]) == 0
    out = capsys.readouterr().out
    assert "gone  0.2" in out


def test_a_string_is_compared_only_where_a_string_row_names_its_file(
    repo: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """A docstring row does not make a file's strings prose, so a lost value there is not named."""
    rule = repo / ".git" / "rule.md"
    rule.write_text(STRING_READERS, encoding="utf-8")
    monkeypatch.setattr(new_prose, "RULE", rule)
    refusal = 'def check(x):\n    raise ValueError("the flow must be at least 0.2 L/min")\n'
    _write(repo, "src/pkg/core/check.py", refusal)
    _git(repo, "add", "-A")
    _git(repo, "commit", "-qm", "refusal")
    _git(repo, "branch", "-f", "main")
    _write(repo, "src/pkg/core/check.py", refusal.replace("at least 0.2 L/min", "too low"))

    out = _compare(repo, capsys)

    assert "gone  0.2" not in out


def test_a_file_is_compared_only_where_a_row_of_the_reader_table_names_it(
    repo: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    rule = repo / ".git" / "rule.md"
    rule.write_text(READERS, encoding="utf-8")
    monkeypatch.setattr(new_prose, "RULE", rule)
    _write(repo, "tests/unit/test_tool.py", "import json\n" + SOURCE)
    _write(repo, "src/pkg/fresh.py", SOURCE)

    out = _compare(repo, capsys)

    # A new file is one passage: three long units and the two-word docstring.
    assert f"src/pkg/fresh.py, rows 1-13: new, {3 * MIN_WORDS + 2} words" in out
    assert "tests/unit/test_tool.py" not in out


def test_a_file_named_only_for_an_unedited_reader_is_not_compared(
    repo: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """An item brief has a reader the rule names, and the comparison still leaves it out."""
    rule = repo / ".git" / "rule.md"
    rule.write_text(READERS.replace("A developer", new_prose.UNEDITED_READERS[0]), encoding="utf-8")
    monkeypatch.setattr(new_prose, "RULE", rule)
    _write(repo, "src/pkg/fresh.py", SOURCE)

    out = _compare(repo, capsys)

    assert out.startswith("No passage of the reviewed files changed its prose")
    assert "src/pkg/fresh.py" not in out


def test_a_file_that_will_not_parse_is_named_and_not_read(
    repo: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    _write(repo, "src/pkg/broken.py", "def f(:\n")

    out = _compare(repo, capsys)

    assert "Not read, because Python would not parse the file:\n  src/pkg/broken.py: " in out


def test_the_tool_runs_only_the_comparison() -> None:
    """The modes that wrote a request for the copy editor were removed with it (`PL-GL45`)."""
    with pytest.raises(SystemExit) as stopped:
        main(["--base", "main"])

    assert stopped.value.code == 2
