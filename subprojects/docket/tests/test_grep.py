"""A `grep` clause's phrase that its file holds only across a line break (`PL-RR1N`).

`grep` reads one line at a time, so a phrase a document wraps is on no line it
reads: the clause fails whether or not the work is done, and under `!` passes
while the phrase is still there. Each case below is a way the reading of "the
same phrase, once the lines are read as one" could find a wrap that `grep`
would not miss, or miss one it would, and each reads a real file the way the
replay and `docket verify` do.
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

from docket.grep import Wrap, read_grep, wrapped
from docket.shell import shell_words

#: `PL-FG9D`'s sentence, wrapped where its author's editor wrapped it.
WRAPPED = (
    "# Machine\n"
    "\n"
    "The fresh-gas inlet contributes exactly two rates and\n"
    "one volume to the breathing circuit, whatever the machine.\n"
)
PHRASE = "contributes exactly two rates and one volume to the breathing circuit"


def _write(root: Path, name: str, text: str) -> None:
    path = root / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _grep_status(root: Path, command: str) -> int:
    """What the shell answers for `command` in `root`, the evidence each case is read against."""
    return subprocess.run(command, shell=True, cwd=root, check=False).returncode


def test_a_verify_phrase_split_by_line_wrapping_is_found_with_its_lines(tmp_path: Path) -> None:
    """`PL-FG9D`'s case: the work was done, and its own `verify:` exited 1."""
    _write(tmp_path, "docs/MODEL.md", WRAPPED)
    command = f"grep -qF '{PHRASE}' docs/MODEL.md"

    assert _grep_status(tmp_path, command) == 1
    assert wrapped(tmp_path, command) == (Wrap(PHRASE, False, "docs/MODEL.md", 3, 4),)


def test_a_removal_the_document_still_holds_across_a_line_break_is_found_negated(
    tmp_path: Path,
) -> None:
    """`PL-Z4WL`'s case: its fix quoted the sentence it removed across two lines of
    `ROADMAP.md`, and its `! grep` passed at its own close-out."""
    _write(
        tmp_path,
        "ROADMAP.md",
        'This paragraph said item 1 did not exist ("has no\n'
        'planned-milestone line of its own") until it was corrected.\n',
    )
    command = (
        "grep -q 'corrected' ROADMAP.md && ! grep -q 'has no planned-milestone line of its' "
        "ROADMAP.md"
    )

    assert _grep_status(tmp_path, command) == 0
    assert wrapped(tmp_path, command) == (
        Wrap("has no planned-milestone line of its", True, "ROADMAP.md", 1, 2),
    )


def test_a_phrase_one_line_of_any_file_holds_is_seen_by_grep_and_not_reported(
    tmp_path: Path,
) -> None:
    _write(tmp_path, "docs/a.md", WRAPPED)
    _write(tmp_path, "docs/b.md", f"It {PHRASE}.\n")
    command = f"grep -qF '{PHRASE}' docs/a.md docs/b.md"

    assert _grep_status(tmp_path, command) == 0
    assert wrapped(tmp_path, command) == ()


def test_list_items_block_quotes_and_lazy_lines_are_read_past_their_markers(tmp_path: Path) -> None:
    """The markers hold the statement rather than belong to it (`markdown.unmarked`)."""
    _write(
        tmp_path,
        "notes.md",
        "- an entry whose sentence runs\n"
        "  on to its second line\n"
        "\n"
        "> a quotation whose sentence runs\n"
        "> on to its second line\n"
        "\n"
        "> a quotation carried on lazily\n"
        "onto an unmarked line\n",
    )

    def found(phrase: str) -> tuple[int, int]:
        (wrap,) = wrapped(tmp_path, f"grep -qF '{phrase}' notes.md")
        return wrap.first, wrap.last

    assert found("entry whose sentence runs on to its") == (1, 2)
    assert found("quotation whose sentence runs on to its") == (4, 5)
    assert found("carried on lazily onto an") == (7, 8)


def test_a_paragraph_break_a_fence_and_a_table_are_not_read_across(tmp_path: Path) -> None:
    """Two statements are not one sentence, and a fence's line ends are its text's own."""
    _write(
        tmp_path,
        "notes.md",
        "The first paragraph ends here.\n"
        "\n"
        "The second begins here.\n"
        "\n"
        "```\n"
        "git push\n"
        "origin main\n"
        "```\n"
        "\n"
        "| one | two |\n"
        "| --- | --- |\n"
        "| three | four |\n",
    )

    for phrase in ("ends here. The second", "git push origin", "two | | --- |"):
        assert wrapped(tmp_path, f"grep -qF '{phrase}' notes.md") == (), phrase


def test_case_is_folded_where_i_folds_it_and_nowhere_else(tmp_path: Path) -> None:
    _write(tmp_path, "notes.md", "The Fresh-Gas\nInlet feeds it.\n")

    assert wrapped(tmp_path, "grep -qF 'fresh-gas inlet' notes.md") == ()
    assert wrapped(tmp_path, "grep -qiF 'fresh-gas inlet' notes.md") == (
        Wrap("fresh-gas inlet", False, "notes.md", 1, 2),
    )


def test_a_dot_reads_as_any_character_and_any_other_pattern_is_left_alone(tmp_path: Path) -> None:
    """Without `-F` a phrase is a pattern: `.` matches any character but a line end, so
    it reads as one; a bracket, an anchor or a repetition is a question of its own."""
    _write(tmp_path, "notes.md", "It wraps after the word\nhere, version 0.6.0 and on.\n")

    assert wrapped(tmp_path, "grep -q 'word here, version 0.6' notes.md") == (
        Wrap("word here, version 0.6", False, "notes.md", 1, 2),
    )
    for pattern in ("word here, [v]ersion", "word here,* version", "^It wraps after the word here"):
        assert wrapped(tmp_path, f"grep -q '{pattern}' notes.md") == (), pattern
    assert wrapped(tmp_path, "grep -qE 'word here, (version)' notes.md") == ()


def test_a_comment_carried_onto_the_next_line_is_read_as_one_outside_markdown(
    tmp_path: Path,
) -> None:
    """A `#` or `#:` comment and a docstring are prose a phrase can be wrapped in too."""
    _write(
        tmp_path,
        "tool.py",
        "#: The options an admitted clause may carry, each changing only\n"
        "#: what matches.\n"
        "FLAGS = 1\n"
        "\n"
        "\n"
        "def run() -> None:\n"
        '    """Read the clause the way grep reads\n'
        '    it, a line at a time."""\n'
        "    # a comment beside code is its own run\n"
        "    x = 1\n",
    )

    assert wrapped(tmp_path, "grep -qF 'changing only what matches' tool.py") == (
        Wrap("changing only what matches", False, "tool.py", 1, 2),
    )
    assert wrapped(tmp_path, "grep -qF 'grep reads it, a line' tool.py") == (
        Wrap("grep reads it, a line", False, "tool.py", 7, 8),
    )
    assert wrapped(tmp_path, "grep -qF 'own run x = 1' tool.py") == ()


def test_globs_and_recursion_read_the_files_grep_reads(tmp_path: Path) -> None:
    """A glob is the shell's; `-r` walks as GNU grep walks, filters and links included."""
    _write(tmp_path, "docs/items/PL-K7QX-a-title.md", WRAPPED)
    _write(tmp_path, "docs/skill/a.md", WRAPPED)
    _write(tmp_path, "docs/skill/b.txt", WRAPPED)
    _write(tmp_path, "elsewhere.md", WRAPPED)
    (tmp_path / "docs" / "linked").mkdir()
    os.symlink(tmp_path / "elsewhere.md", tmp_path / "docs" / "linked" / "c.md")

    assert wrapped(tmp_path, f"grep -qF '{PHRASE}' docs/items/PL-K7QX-*.md") == (
        Wrap(PHRASE, False, "docs/items/PL-K7QX-a-title.md", 3, 4),
    )
    assert wrapped(tmp_path, f"grep -rqF --include='*.txt' '{PHRASE}' docs/skill/") == (
        Wrap(PHRASE, False, "docs/skill/b.txt", 3, 4),
    )
    # The last filter to match a file decides it, and one no filter matches is
    # read unless the first filter is an `--include`.
    last_wins = f"grep -rqF --exclude='a.md' --include='*.md' '{PHRASE}' docs/skill/"
    assert wrapped(tmp_path, last_wins) == (Wrap(PHRASE, False, "docs/skill/a.md", 3, 4),)
    first_include = f"grep -rqF --include='*.md' --exclude='a.md' '{PHRASE}' docs/skill/"
    assert wrapped(tmp_path, first_include) == ()
    assert wrapped(tmp_path, f"grep -rqF '{PHRASE}' docs/linked") == ()
    assert wrapped(tmp_path, f"grep -qF '{PHRASE}' docs/skill/") == ()


def test_only_a_grep_clause_s_phrase_is_read(tmp_path: Path) -> None:
    """A coverage run, a refused command and a phrase no line break can split say nothing."""
    _write(tmp_path, "notes.md", "one-word\nphrases.\n")

    for command in (
        "uv run pytest --cov=docket.grep --cov-fail-under=100",
        "bin/docket wave | grep -q 'one-word phrases'",
        "grep -qF 'phrases.' notes.md",
        "grep -qv 'one-word phrases' notes.md",
    ):
        assert wrapped(tmp_path, command) == (), command


def test_the_shape_check_and_the_wrap_reading_read_one_clause_one_way() -> None:
    """`checks._grep_refusal` reads its verdict from `read_grep`, so the clause the shape
    check admits is the clause whose pattern and files `wrapped` reads."""
    (clause,) = shell_words(
        "! grep -rqiF --include='*.md' --exclude=a.md -- '-x y' docs/ b.md"
    ).clauses
    parsed = read_grep([token for token in clause.tokens if not isinstance(token, str)])

    assert not isinstance(parsed, str)
    assert parsed.negated
    assert parsed.letters == frozenset("rqiF")
    assert parsed.filters == ((True, "*.md"), (False, "a.md"))
    assert parsed.pattern == "-x y"
    assert [word.text for word in parsed.paths] == ["docs/", "b.md"]
