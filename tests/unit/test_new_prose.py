"""`tools/new_prose.py` must print the long simulator prose a branch changed, and nothing else.

The close-out reviewer opens no file, so a unit this tool leaves out is never
reviewed and nothing says so. These tests pin which files count as the
simulator's, which units count as changed, the word threshold, and the line
that names a file the tool could not read.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import new_prose
import pytest
from docket.config import load
from new_prose import (
    MIN_WORDS,
    PROMPT,
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
)

LONG = " ".join(["word"] * MIN_WORDS)
SHORT = " ".join(["word"] * (MIN_WORDS - 1))

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


def test_only_a_long_unit_that_a_changed_row_falls_inside_is_printed(repo: Path) -> None:
    model = repo / "src/pkg/model.py"
    # A change to code beside a long docstring, a change inside a short one,
    # and a change inside a long comment.
    text = SOURCE.replace("x * LIMIT", "x * LIMIT * 2").replace(
        f'"""{SHORT}"""', f'"""{SHORT} more"""'
    )
    model.write_text(text.replace(f"# {LONG}", f"# {LONG} too"), encoding="utf-8")

    found = branch_prose(repo, "main")

    # The short docstring now has 30 words, so it is printed too.
    assert [(unit.kind, unit.first) for unit in found.units] == [("docstring", 12), ("comment", 13)]
    assert found.unread == []


def test_a_new_file_has_every_long_unit_printed(repo: Path) -> None:
    _write(repo, "src/pkg/fresh.py", SOURCE)

    found = branch_prose(repo, "main")

    assert [(unit.path, unit.first) for unit in found.units] == [
        ("src/pkg/fresh.py", 1),
        ("src/pkg/fresh.py", 7),
        ("src/pkg/fresh.py", 13),
    ]


def test_a_test_file_is_the_simulators_only_when_it_imports_the_product(repo: Path) -> None:
    _write(repo, "tests/unit/test_tool.py", "import json\n" + SOURCE)
    _write(repo, "tests/unit/test_sim.py", "import anesthesia_sim\n" + SOURCE)
    _write(repo, "tools/script.py", SOURCE)

    found = branch_prose(repo, "main")

    assert {unit.path for unit in found.units} == {"tests/unit/test_sim.py"}


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


def test_main_says_so_when_nothing_long_changed(
    repo: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    (repo / "src/pkg/model.py").write_text(SOURCE.replace("LIMIT = 3", "LIMIT = 4"), "utf-8")

    assert main(["--root", str(repo), "--base", "main"]) == 0
    assert capsys.readouterr().out.startswith(
        "No docstring, comment or document paragraph of 30 words or more"
    )


def test_main_numbers_each_unit_with_its_rows(
    repo: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    _write(repo, "src/pkg/fresh.py", SOURCE)

    assert main(["--root", str(repo), "--base", "main"]) == 0
    out = capsys.readouterr().out
    prompt = PROMPT.read_text(encoding="utf-8")
    assert out.startswith(prompt)
    assert out[len(prompt) :].startswith(
        "\n3 docstrings, comments and document paragraphs of 30 words or more changed"
    )
    assert f"[1] src/pkg/fresh.py, rows 1-1, docstring, {MIN_WORDS} words" in out
    assert "[3] src/pkg/fresh.py, rows 13-13, comment" in out


def _commit(repo: Path, message: str) -> str:
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "--allow-empty", "-m", message)
    return _git(repo, "rev-parse", "HEAD").strip()


def _count(repo: Path, capsys: pytest.CaptureFixture[str], *extra: str) -> tuple[int, str]:
    code = main(["--root", str(repo), "--base", "main", "--count", *extra])
    return code, capsys.readouterr().out.strip()


def test_counts_units_since_commit(repo: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """`--count` counts committed long units, leaving out those already at a given commit.

    This is what `bin/docket arm` reads (`PL-W04Z`). A code fix after the
    review must not ask for a second review, and a new long unit must.
    """
    _write(repo, "src/pkg/fresh.py", SOURCE)
    _commit(repo, "add a file with three long units")
    assert _count(repo, capsys) == (0, "3")

    reviewed = _commit(repo, "record the review")
    (repo / "src/pkg/fresh.py").write_text(SOURCE.replace("x * LIMIT", "x * LIMIT * 2"), "utf-8")
    _commit(repo, "a code fix beside a reviewed docstring")
    assert _count(repo, capsys, reviewed) == (0, "0")

    _write(repo, "src/pkg/fresh.py", SOURCE + f'\n\ndef later():\n    """{LONG} again"""\n')
    _commit(repo, "a new long docstring")
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
    """`bin/docket arm` runs this tool under the project interpreter, which parses all of `src/`.

    A bare `python3` is the tools interpreter, held to a 3.11 floor, and `src/`
    targets 3.14. Under the bare one the count exits 2 on any branch that
    changes a file written in newer syntax, such as the PEP 758 `except` in
    `app_metadata.py`, and `arm` then holds correct work (`PL-Q508`).
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
    assert f"[1] src/pkg/fresh.py, rows 1-1, docstring, {MIN_WORDS} words, for: A developer" in out
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


def test_a_unit_whose_file_no_row_names_stops_the_report(
    repo: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    rule = tmp_path / "rule.md"
    rule.write_text(READERS.replace("Code in `src/`", "Code in `lib/`"), encoding="utf-8")
    monkeypatch.setattr(new_prose, "RULE", rule)
    _write(repo, "src/pkg/fresh.py", SOURCE)

    assert main(["--root", str(repo), "--base", "main"]) == 1
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "no row of the reader table in rule.md names src/pkg/fresh.py" in captured.err


@pytest.mark.parametrize(
    "path",
    [
        "src/anesthesia_sim/core/patient.py",
        "tests/unit/test_patient.py",
        "docs/MODEL.md",
        "README.md",
    ],
)
def test_the_rule_names_a_reader_for_every_kind_of_file_the_review_reads(path: str) -> None:
    """A rule edit that drops a row would stop every review of that kind of file."""
    assert readers_of(reader_table(RULE.read_text(encoding="utf-8")), path)


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

    assert "1 passages of the simulator's files changed their prose" in out
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

    assert "No passage of the simulator's files changed its prose" in _compare(precise, capsys)


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
