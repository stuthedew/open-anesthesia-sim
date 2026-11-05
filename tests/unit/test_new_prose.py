"""`tools/new_prose.py` must print the long prose a branch changed, inside its section.

The copy-editing agent, `.claude/agents/copy-editor.md`, reads only this
tool's output, so a passage this tool leaves out is never reviewed and nothing
says so. These tests pin which files the reader table in
`.claude/rules/plain-writing.md` names, which paragraphs, table rows,
docstrings and comments count as changed, the word threshold, which rows the
agent may rewrite, and the lines that name a file the tool did not review or
could not read.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import new_prose
import pytest
from docket.config import load
from new_prose import (
    ROOT,
    RULE,
    Unit,
    branch_prose,
    document_units,
    excerpt,
    main,
    prose_units,
    reader_table,
    readers_of,
    reviews_of,
)

#: The number of words in `LONG`, which only has to be longer than `SHORT`. The
#: review reads units of any length, so it treats the two alike.
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


def test_only_a_unit_that_a_changed_row_falls_inside_is_printed(repo: Path) -> None:
    model = repo / "src/pkg/model.py"
    # Change code beside a docstring, and the text inside a short docstring
    # and a long comment.
    text = SOURCE.replace("x * LIMIT", "x * LIMIT * 2").replace(
        f'"""{SHORT}"""', f'"""{SHORT} more"""'
    )
    model.write_text(text.replace(f"# {LONG}", f"# {LONG} too"), encoding="utf-8")

    found = branch_prose(repo, "main")

    # The short docstring is printed: the review reads a unit of any length.
    assert [(unit.kind, unit.first) for unit in found.units] == [("docstring", 12), ("comment", 13)]
    assert found.unread == []


def test_a_new_file_has_every_unit_printed_short_ones_included(repo: Path) -> None:
    _write(repo, "src/pkg/fresh.py", SOURCE)

    found = branch_prose(repo, "main")

    assert [(unit.path, unit.first) for unit in found.units] == [
        ("src/pkg/fresh.py", 1),
        ("src/pkg/fresh.py", 7),
        ("src/pkg/fresh.py", 12),
        ("src/pkg/fresh.py", 13),
    ]


def test_a_file_is_read_only_where_a_row_of_the_reader_table_names_it(
    repo: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    rule = repo / ".git" / "rule.md"
    rule.write_text(READERS, encoding="utf-8")
    monkeypatch.setattr(new_prose, "RULE", rule)
    _write(repo, "tests/unit/test_tool.py", "import json\n" + SOURCE)
    _write(repo, "src/pkg/fresh.py", SOURCE)

    found = branch_prose(repo, "main")

    assert {unit.path for unit in found.units} == {"src/pkg/fresh.py"}


def test_a_file_that_will_not_parse_is_named_and_not_read(repo: Path) -> None:
    _write(repo, "src/pkg/broken.py", "def f(:\n")

    found = branch_prose(repo, "main")

    assert found.units == []
    assert len(found.unread) == 1
    assert found.unread[0].startswith("src/pkg/broken.py: ")


def test_excerpt_marks_the_unit_and_the_code_around_it() -> None:
    lines = [f"line {row}" for row in range(1, 21)]

    shown = list(excerpt(lines, Unit("src/f.py", "comment", 10, 11, "")))

    assert shown[0] == "    6 | line 6"
    assert shown[4:6] == ["   10 > line 10", "   11 > line 11"]
    assert shown[-1] == "   15 | line 15"


def test_main_says_so_when_no_prose_changed(repo: Path, capsys: pytest.CaptureFixture[str]) -> None:
    (repo / "src/pkg/model.py").write_text(SOURCE.replace("LIMIT = 3", "LIMIT = 4"), "utf-8")

    assert main(["--root", str(repo), "--base", "main"]) == 0
    assert capsys.readouterr().out.startswith(
        "No passage changed in a file that the reader table names"
    )


def test_main_numbers_each_unit_with_its_rows(
    repo: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    _write(repo, "src/pkg/fresh.py", SOURCE)

    assert main(["--root", str(repo), "--base", "main"]) == 0
    out = capsys.readouterr().out
    rule = RULE.read_text(encoding="utf-8").rstrip("\n")
    assert out.startswith(rule)
    assert out[len(rule) :].startswith(
        "\n\nThe writing rule ends here, and the prose to review follows.\n\n4 passages changed"
    )
    assert "src/pkg/fresh.py, rows 1-5:\n" in out
    assert f"[1] src/pkg/fresh.py, rows 1-1. Changed text: new, {MIN_WORDS} words." in out
    assert "[4] src/pkg/fresh.py, rows 13-13." in out
    assert f"   13 >     # {LONG}\n   14 |     return y" in out


def _commit(repo: Path, message: str) -> str:
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "--allow-empty", "-m", message)
    return _git(repo, "rev-parse", "HEAD").strip()


def _count(repo: Path, capsys: pytest.CaptureFixture[str], *extra: str) -> tuple[int, str]:
    code = main(["--root", str(repo), "--base", "main", "--count", *extra])
    return code, capsys.readouterr().out.strip()


def test_counts_units_since_commit(repo: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """The `--count` option counts committed units, leaving out those already at a given commit.

    The workflow command `bin/docket arm` reads this count (`PL-W04Z`). A code fix
    after the review must not trigger a second review, and a new unit must.
    """
    _write(repo, "src/pkg/fresh.py", SOURCE)
    _commit(repo, "add a file with four units")
    assert _count(repo, capsys) == (0, "4")

    reviewed = _commit(repo, "record the review")
    (repo / "src/pkg/fresh.py").write_text(SOURCE.replace("x * LIMIT", "x * LIMIT * 2"), "utf-8")
    _commit(repo, "a code fix beside a reviewed docstring")
    assert _count(repo, capsys, reviewed) == (0, "0")

    _write(repo, "src/pkg/fresh.py", SOURCE + f'\n\ndef later():\n    """{LONG} again"""\n')
    _commit(repo, "a new docstring")
    assert _count(repo, capsys, reviewed) == (0, "1")


def test_count_reads_the_commits_and_not_the_working_tree(
    repo: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    _write(repo, "src/pkg/fresh.py", SOURCE)

    assert _count(repo, capsys) == (0, "0")


def test_count_leaves_out_prose_a_merge_of_the_base_brings_in(
    repo: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    reviewed = _commit(repo, "a review with nothing to review")
    _git(repo, "checkout", "-q", "main")
    _write(repo, "src/pkg/other.py", SOURCE)
    _commit(repo, "someone else's long prose")
    _git(repo, "checkout", "-q", "work")
    _git(repo, "merge", "-q", "--no-edit", "main")

    assert _count(repo, capsys, reviewed) == (0, "0")


def test_count_exits_2_when_a_changed_file_will_not_parse(
    repo: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    _write(repo, "src/pkg/broken.py", "def f(:\n")
    _commit(repo, "a file Python refuses")

    assert main(["--root", str(repo), "--base", "main", "--count"]) == 2
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "src/pkg/broken.py" in captured.err


def test_arm_counts_prose_under_the_interpreter_src_targets() -> None:
    """The workflow command `bin/docket arm` runs this tool under the project interpreter.

    That interpreter parses all of `src/`, which targets 3.14. A bare `python3`
    runs `tools/` and may be as old as 3.11. Under such an interpreter, the
    count fails with exit status 2 on any branch that changes a file written in
    newer syntax, such as the PEP 758 `except` in `app_metadata.py`. The
    workflow command then blocks correct work (`PL-Q508`).
    """
    command = load(ROOT).prose_count_command.split()
    assert command[:3] == ["uv", "run", "python"]
    assert "tools/new_prose.py" in command


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
    """A heading, a fence and an HTML comment hold no prose to review, and a table row does."""
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


@pytest.fixture
def documented(repo: Path) -> Path:
    """`repo` with `DOCUMENT` committed as `docs/MODEL.md` on `main`, and `work` checked out."""
    _git(repo, "checkout", "-q", "main")
    _write(repo, "docs/MODEL.md", DOCUMENT)
    _write(repo, "docs/other.md", DOCUMENT)
    _commit(repo, "add the model document")
    _git(repo, "checkout", "-q", "work")
    _git(repo, "merge", "-q", "main")
    return repo


def test_a_changed_long_paragraph_of_the_model_document_is_printed(documented: Path) -> None:
    """Only the changed paragraph is printed, and a document outside the two is not read."""
    model = documented / "docs/MODEL.md"
    model.write_text(DOCUMENT.replace(f"- {LONG}", f"- {LONG} more"), encoding="utf-8")
    other = documented / "docs/other.md"
    other.write_text(DOCUMENT.replace(f"- {LONG}", f"- {LONG} more"), encoding="utf-8")

    found = branch_prose(documented, "main")

    assert [(unit.path, unit.kind, unit.first) for unit in found.units] == [
        ("docs/MODEL.md", "paragraph", 5)
    ]


def test_count_counts_a_new_model_paragraph_and_leaves_out_a_reviewed_one(
    documented: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    model = documented / "docs/MODEL.md"
    model.write_text(DOCUMENT + f"\n{LONG} added\n", encoding="utf-8")
    reviewed = _commit(documented, "a new long paragraph, then its review")
    assert _count(documented, capsys) == (0, "1")
    assert _count(documented, capsys, reviewed) == (0, "0")

    model.write_text(DOCUMENT + f"\n{LONG} added\n\n| a | {LONG} b |\n", encoding="utf-8")
    _commit(documented, "a table row the review did not see")
    assert _count(documented, capsys, reviewed) == (0, "1")


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


def test_each_unit_names_its_reader(
    repo: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    rule = tmp_path / "rule.md"
    rule.write_text(READERS, encoding="utf-8")
    monkeypatch.setattr(new_prose, "RULE", rule)
    _write(repo, "src/pkg/fresh.py", SOURCE)

    assert main(["--root", str(repo), "--base", "main"]) == 0
    out = capsys.readouterr().out
    assert (
        f"[1] src/pkg/fresh.py, rows 1-1. Changed text: new, {MIN_WORDS} words. For: A developer"
        in out
    )
    assert (
        "\n".join(
            [
                "Readers of src/pkg/fresh.py:",
                "  - A developer.",
                "    Knows: Python.",
                "    Does not know: Our history.",
                "    Will: Change the code.",
            ]
        )
        in out
    )


def test_a_passage_in_a_file_no_row_names_is_listed_as_not_reviewed(
    repo: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """A file nobody has named a reader for is said to be unreviewed, never passed over."""
    rule = repo / ".git" / "rule.md"
    rule.write_text(READERS.replace("Code in `src/`", "Code in `lib/`"), encoding="utf-8")
    monkeypatch.setattr(new_prose, "RULE", rule)
    _write(repo, "src/pkg/fresh.py", SOURCE)

    assert main(["--root", str(repo), "--base", "main"]) == 0
    out = capsys.readouterr().out
    assert out.startswith("No passage changed")
    assert out.endswith(
        "Not reviewed, because no row of the reader table in rule.md names it:\n"
        "  src/pkg/fresh.py\n"
    )


@pytest.mark.parametrize(
    "path",
    [
        "src/anesthesia_sim/core/patient.py",
        "tests/unit/test_patient.py",
        "docs/MODEL.md",
        "README.md",
        "docs/items/PL-22T5-close-out-s-prose-review-reads-only-the.md",
        ".claude/rules/plain-writing.md",
        ".claude/agents/copy-editor.md",
        "tools/new_prose.py",
        "subprojects/docket/src/docket/arming.py",
        "CLAUDE.md",
    ],
)
def test_the_rule_names_a_reader_for_every_kind_of_file_the_review_reads(path: str) -> None:
    """A rule edit that drops a row would stop every review of that kind of file."""
    assert readers_of(reader_table(RULE.read_text(encoding="utf-8")), path)


#: The product document that the reader table leaves out on purpose. The rule's
#: paragraph under the table gives the reason: `bin/docket release` writes each
#: note from item titles.
UNREVIEWED_PRODUCT_DOCUMENTS = ("docs/releases",)


def test_every_product_document_has_a_reader_except_the_release_notes() -> None:
    """A product document added without a row would get no copy edit for its reader."""
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
    """A release note edited by the copy editor would no longer match its item's title."""
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
    so, and a trial copy editor dropped a value from a condition (`PL-J1ZM`).
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


@pytest.mark.parametrize("kind", ["replies", "pull request titles and bodies"])
def test_the_rule_names_a_reader_for_each_kind_of_draft(kind: str) -> None:
    """Close-out and the reply rule pass these words to `--kind`."""
    assert any(kind in reader.kind.casefold() for reader in new_prose.rule_table())


#: A document whose first section holds four long paragraphs.
SECTIONS = f"""\
# Model

## Displayed precision

{LONG} first.

{LONG} second.

{LONG} third.

{LONG} fourth.

## Next

{LONG} other.
"""


@pytest.fixture
def sectioned(repo: Path) -> Path:
    """`repo` with `SECTIONS` committed as `docs/MODEL.md` on `main`, and `work` checked out."""
    _git(repo, "checkout", "-q", "main")
    _write(repo, "docs/MODEL.md", SECTIONS)
    _commit(repo, "add the model document")
    _git(repo, "checkout", "-q", "work")
    _git(repo, "merge", "-q", "main")
    return repo


def _review(repo: Path, capsys: pytest.CaptureFixture[str]) -> str:
    assert main(["--root", str(repo), "--base", "main"]) == 0
    return capsys.readouterr().out


def test_a_changed_paragraph_is_shown_in_its_whole_section_with_one_neighbour_each_side(
    sectioned: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """The copy editor reads the section, and may rewrite the change and the unit on each side."""
    changed = SECTIONS.replace("third.", "third, changed.")
    (sectioned / "docs/MODEL.md").write_text(changed, encoding="utf-8")

    out = _review(sectioned, capsys)

    assert 'docs/MODEL.md § "Displayed precision", rows 3-12:\n    3 | ## Displayed' in out
    assert ("[1] docs/MODEL.md, rows 7-11. Changed text: 31 words on main, 32 now, 1 more.") in out
    assert f"    5 | {LONG} first.\n    6 | \n" in out
    assert f"    7 > {LONG} second.\n    8 > \n    9 > {LONG} third, changed." in out
    assert f"   11 > {LONG} fourth.\n   12 | \n" in out
    assert "other." not in out.partition("The writing rule ends here")[2]


def test_two_changes_that_would_share_a_neighbour_are_one_passage(
    sectioned: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    changed = SECTIONS.replace("first.", "first, changed.").replace("third.", "third, changed.")
    (sectioned / "docs/MODEL.md").write_text(changed, encoding="utf-8")

    out = _review(sectioned, capsys)

    assert "[1] docs/MODEL.md, rows 5-11. Changed text: 62 words on main, 64 now, 2 more." in out
    assert "[2]" not in out


def test_front_matter_is_not_read_as_a_heading() -> None:
    """Read as Markdown, the closing `---` of front matter underlines a heading."""
    source = f"---\nid: PL-K7QX\ntitle: A title\n---\n\n{LONG}\n"

    (review,) = reviews_of("docs/items/PL-K7QX.md", None, source, "")

    assert (review.section, review.first, review.top) == ("", 1, 6)


def test_draft_prints_the_rule_the_readers_of_its_kind_and_the_file_as_one_passage(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    rule = tmp_path / "rule.md"
    rule.write_text(READERS, encoding="utf-8")
    monkeypatch.setattr(new_prose, "RULE", rule)
    draft = tmp_path / "reply.md"
    draft.write_text("Line one.\n\nLine two.\n", encoding="utf-8")

    assert main(["--draft", str(draft), "--kind", "replies"]) == 0
    out = capsys.readouterr().out
    assert out.startswith(READERS.rstrip("\n"))
    shown = out.partition("The writing rule ends here")[2]
    assert "Readers of replies:\n  - The owner.\n" in shown
    assert "A developer" not in shown
    assert "[1] reply.md, rows 1-3. Draft: 4 words. For: The owner\n" in shown
    assert "    1 > Line one.\n    2 > \n    3 > Line two." in shown

    assert main(["--draft", str(draft), "--kind", "sonnets"]) == 1
    assert "no row of the reader table in rule.md has 'sonnets'" in capsys.readouterr().err


#: A model document whose section holds a subsection.
NESTED = f"""\
---
title: front matter
---

# Model

## Displayed precision

{LONG} first.

### Readouts

{LONG} second.

## Next

{LONG} other.

"""


@pytest.fixture
def nested(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """A repository root holding `NESTED` as `docs/MODEL.md`, with `READERS` as the rule file."""
    rule = tmp_path / "rule.md"
    rule.write_text(READERS, encoding="utf-8")
    monkeypatch.setattr(new_prose, "RULE", rule)
    _write(tmp_path, "docs/MODEL.md", NESTED)
    return tmp_path


def test_section_prints_a_section_and_its_subsections_as_one_passage_to_rewrite(
    nested: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """The copy editor may rewrite the whole section, to merge a fact repeated across paragraphs."""
    argv = ["--root", str(nested), "--section", "docs/MODEL.md", "--heading", "Displayed precision"]

    assert main(argv) == 0

    out = capsys.readouterr().out
    shown = out.partition("The writing rule ends here")[2]
    assert "Readers of docs/MODEL.md:\n  - A clinician.\n" in shown
    assert "  - A forker.\n" in shown
    assert "The owner" not in shown
    assert (
        '[1] docs/MODEL.md § "Displayed precision", rows 7-13. Whole section: 67 words. '
        "For: A clinician; A forker\n"
    ) in shown
    assert f"    7 > ## Displayed precision\n    8 > \n    9 > {LONG} first." in shown
    assert f"   13 > {LONG} second." in shown
    assert "other." not in shown
    assert "|" not in shown.partition("[1]")[2]


def test_section_without_a_heading_is_refused_and_names_the_two_part_review(
    nested: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """A whole document is never line-edited in one request (project owner, 2026-11-04)."""
    with pytest.raises(SystemExit) as stopped:
        main(["--root", str(nested), "--section", "docs/MODEL.md"])

    assert stopped.value.code == 2
    assert "tools/copy_edit.py --structure FILE, then --sections FILE" in capsys.readouterr().err


def test_each_section_s_own_rows_are_one_part_and_a_heading_alone_is_none() -> None:
    lines = new_prose.markdown_lines(NESTED)

    assert new_prose.own_parts(lines) == [
        new_prose.Part("Displayed precision", 7, 9),
        new_prose.Part("Readouts", 11, 13),
        new_prose.Part("Next", 15, 17),
    ]


def test_a_document_within_the_limit_is_one_chapter() -> None:
    lines = new_prose.markdown_lines(NESTED)

    assert new_prose.chapters(lines, limit=1000) == [new_prose.Part("", 5, 17)]


def test_a_longer_document_splits_by_level_and_keeps_every_row_once() -> None:
    """A heading with no text of its own goes with its first subsection, and no row is lost."""
    lines = new_prose.markdown_lines(NESTED)

    found = new_prose.chapters(lines, limit=40)

    assert found == [
        new_prose.Part("Displayed precision", 5, 9),
        new_prose.Part("Readouts", 11, 13),
        new_prose.Part("Next", 15, 17),
    ]


def test_a_section_with_no_subsection_is_cut_into_runs_of_whole_blocks() -> None:
    lines = new_prose.markdown_lines(f"# Long\n\n{LONG}\n\n```\ncode\n\nmore\n```\n\n{LONG}\n")

    found = new_prose.chapters(lines, limit=MIN_WORDS + 5)

    assert found == [
        new_prose.Part("Long (run 1 of 2)", 1, 9),
        new_prose.Part("Long (run 2 of 2)", 11, 11),
    ]


def test_a_structure_read_marks_every_row_read_only(nested: Path) -> None:
    [(part, request)] = new_prose.structure_reports(nested, "docs/MODEL.md", new_prose.rule_table())

    assert part == new_prose.Part("", 5, 17)
    assert request.startswith(new_prose.STRUCTURE_READ + "\n")
    assert "[1] docs/MODEL.md, rows 5-17. Whole document: 102 words." in request
    assert "    5 | # Model" in request
    assert " > " not in request.partition("[1]")[2]


def test_a_long_document_s_structure_read_is_one_request_per_chapter(
    nested: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(new_prose, "REQUEST_LIMIT_WORDS", 40)

    found = new_prose.structure_reports(nested, "docs/MODEL.md", new_prose.rule_table())

    assert [part.title for part, _ in found] == ["Displayed precision", "Readouts", "Next"]
    assert all(request.startswith(new_prose.CHAPTER_READ) for _, request in found)
    assert '[1] docs/MODEL.md § "Readouts", rows 11-13. Whole section' in found[1][1]


def test_each_section_is_a_request_of_its_own_rows_to_rewrite(nested: Path) -> None:
    found = new_prose.part_reports(nested, "docs/MODEL.md", new_prose.rule_table())

    assert [part.title for part, _ in found] == ["Displayed precision", "Readouts", "Next"]
    first = found[0][1].partition("[1]")[2]
    assert f"    9 > {LONG} first." in first
    assert "second." not in first


def test_the_outline_request_indents_each_chapter_s_outline_under_its_place(nested: Path) -> None:
    outlines = [(new_prose.Part("Readouts", 11, 13), "rows 13: a point.\n\nrows 14: another.")]

    text = new_prose.outline_report("docs/MODEL.md", new_prose.rule_table(), outlines)

    assert text.startswith(new_prose.OUTLINE_READ + "\n")
    assert "[1] docs/MODEL.md, the outlines of its 1 chapters. For: A clinician; A forker" in text
    assert text.endswith(
        'Chapter: docs/MODEL.md § "Readouts", rows 11-13\n  rows 13: a point.\n  rows 14: another.'
    )


@pytest.mark.parametrize(
    ("asked", "reason"),
    [
        (["--section", "docs/MODEL.md", "--heading", "Nowhere"], "0 headings read 'Nowhere'"),
        (["--section", "src/step.py", "--heading", "X"], "src/step.py is not a Markdown file"),
    ],
)
def test_section_refuses_a_heading_it_cannot_find_and_a_file_that_is_not_markdown(
    nested: Path, capsys: pytest.CaptureFixture[str], asked: list[str], reason: str
) -> None:
    assert main(["--root", str(nested), *asked]) == 1

    assert reason in capsys.readouterr().err


def test_section_refuses_a_file_that_no_reader_row_names(
    nested: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    _write(nested, "docs/OTHER.md", NESTED)

    assert main(["--root", str(nested), "--section", "docs/OTHER.md", "--heading", "Next"]) == 1

    assert "no row of the reader table names docs/OTHER.md" in capsys.readouterr().err


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


def test_a_long_interface_string_literal_is_printed_for_its_own_reader(
    repo: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """The notice goes to the learner, and the docstring beside it to the developer."""
    rule = tmp_path / "rule.md"
    rule.write_text(STRING_READERS, encoding="utf-8")
    monkeypatch.setattr(new_prose, "RULE", rule)
    _write(repo, "src/pkg/app/notice.py", NOTICE)

    assert main(["--root", str(repo), "--base", "main"]) == 0
    out = capsys.readouterr().out
    assert (
        f"[1] src/pkg/app/notice.py, rows 2-2. Changed text: new, {MIN_WORDS} words. "
        "For: A developer\n" in out
    )
    assert (
        f"[2] src/pkg/app/notice.py, rows 3-3. Changed text: new, {MIN_WORDS + 2} words. "
        "For: A learner\n" in out
    )


def test_a_short_notice_is_printed_and_a_one_word_string_is_not(
    repo: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A notice of two words is prose a learner reads. A one-word string is a value the code uses.

    The review reads a changed passage of any length (project owner,
    2026-11-04, `PL-HGZS`), but a rewrite of `"mL/h"` or a dictionary key would
    change what the program does.
    """
    rule = tmp_path / "rule.md"
    rule.write_text(STRING_READERS, encoding="utf-8")
    monkeypatch.setattr(new_prose, "RULE", rule)
    _write(repo, "src/pkg/app/units.py", 'RATE = {"unit": "mL/h"}\nPAUSED = "Simulation paused."\n')

    found = branch_prose(repo, "main")

    assert [(unit.kind, unit.text) for unit in found.units] == [("string", "Simulation paused.")]


def test_reviewable_needs_two_words_of_a_string_and_one_of_anything_else() -> None:
    assert new_prose.reviewable(Unit("a.md", "paragraph", 1, 1, "Paused."))
    assert new_prose.reviewable(Unit("a.py", "comment", 1, 1, "why"))
    assert not new_prose.reviewable(Unit("a.py", "string", 1, 1, "mL/h"))
    assert new_prose.reviewable(Unit("a.py", "string", 1, 1, "Simulation paused."))
    assert not new_prose.reviewable(Unit("a.md", "table row", 1, 1, ""))


def test_a_long_string_is_not_printed_where_no_string_row_names_its_file(
    repo: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A docstring row does not send a file's strings to the copy editor."""
    rule = repo / ".git" / "rule.md"
    rule.write_text(STRING_READERS, encoding="utf-8")
    monkeypatch.setattr(new_prose, "RULE", rule)
    _write(repo, "src/pkg/core/notice.py", NOTICE)

    found = branch_prose(repo, "main")

    assert [(unit.kind, unit.first) for unit in found.units] == [("docstring", 2)]


def test_a_refusal_that_loses_its_value_is_reported(
    repo: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """A copy edit that drops the number a refusal names is caught by the comparison."""
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


def test_a_row_reads_back_as_its_number_mark_and_text() -> None:
    assert new_prose.read_row(new_prose.row_line(7, ">", "Some text.")) == (7, ">", "Some text.")
    assert new_prose.read_row(new_prose.row_line(123456, "|", "")) == (123456, "|", "")
    assert new_prose.read_row("Readers of docs/MODEL.md:") is None
    assert new_prose.read_row("   12 * not a mark") is None


def test_a_header_gives_its_passage_number_and_a_title_gives_none() -> None:
    header = f"[3] {new_prose.rows_span('doc.md', 4, 9)}. Draft: 5 words. For: A reader"
    title = f"{new_prose.rows_span('doc.md § "Part"', 1, 20)}:"

    assert new_prose.passage_number(header) == 3
    assert new_prose.read_span(header) == (4, 9)
    assert new_prose.respan(header, 4, 6).startswith("[3] doc.md, rows 4-6. Draft:")
    assert new_prose.passage_number(title) is None
    assert new_prose.passage_number("[x] doc.md, rows 1-2.") is None
    assert new_prose.passage_number("[3] keep") is None
