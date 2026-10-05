"""Where bash ends a line of a script, and how `shell_words` reads the newlines inside one.

A workflow step's script reaches bash whole, so `tools/doc_check.py` cuts it with
`shell.script_lines` rather than a line at a time, which read a here-document's
body as commands and declined a command continued past its line (`PL-Q9LK`).
Every shape below was run through bash 5.2.21 first; the one place this reading
departs from it, a body its delimiter never ends, is pinned as the departure.
"""

from __future__ import annotations

import pytest

from docket.shell import Word, joined_text, script_lines, shell_words


def _words(command: str) -> list[str]:
    reading = shell_words(command)
    return [
        token.text
        for clause in reading.every_clause()
        for token in clause.tokens
        if isinstance(token, Word)
    ]


@pytest.mark.parametrize(
    ("script", "pieces"),
    [
        # A here-document's body and delimiter are input, not lines.
        ("cat <<'PY'\nbin/gone\nPY\nnext\n", ["cat <<'PY'", "next"]),
        # `<<-` strips the tabs before its delimiter, and `<<` does not.
        ("cat <<-EOF\n\tbody\n\tEOF\nnext\n", ["cat <<-EOF", "next"]),
        ("cat <<EOF\n\tEOF\nEOF\nnext\n", ["cat <<EOF", "next"]),
        # Two on a line take their bodies in turn.
        ("cat <<A <<'B'\na\nA\nb\nB\nnext\n", ["cat <<A <<'B'", "next"]),
        # A here-string, and a `<<` inside quotes, open no body.
        ("cat <<<x\necho '<<y'\nnext\n", ["cat <<<x", "echo '<<y'", "next"]),
        # A backslash-newline, a quote and a `$( )` each carry a line on.
        ("a \\\n  b\nnext\n", ["a \\\n  b", "next"]),
        ('echo "x\ny" z\nnext\n', ['echo "x\ny" z', "next"]),
        ("v=$(\n  ls\n)\nnext\n", ["v=$(\n  ls\n)", "next"]),
        # An apostrophe in a comment opens no quote.
        ("# don't\nnext\n", ["# don't", "next"]),
        # A body inside a substitution stays in its line, for `shell_words` to skip.
        (
            'git commit -m "$(cat <<\'EOF\'\nsay "hi"\nEOF\n)"\nnext\n',
            ['git commit -m "$(cat <<\'EOF\'\nsay "hi"\nEOF\n)"', "next"],
        ),
        # A quoted delimiter's body keeps its lines, and an even run of
        # backslashes continues none, so `EOF` ends each body (`PL-2JYP`).
        ("cat <<'EOF'\nabc\\\nEOF\nnext\n", ["cat <<'EOF'", "next"]),
        ("cat <<EOF\nab\\\\\nEOF\nnext\n", ["cat <<EOF", "next"]),
        # `case` is a word away from a command's head, so its `)` closes.
        ("x=$(echo case a in a)\nnext\n", ["x=$(echo case a in a)", "next"]),
        # `((` whose `)` is not followed by another is two subshells, whose
        # newline ends a line as any other does.
        ("((echo a\necho b) )\nnext\n", ["((echo a", "echo b) )", "next"]),
        # Inside `[[ ]]` a newline ends no line, but the bodies waiting on it start.
        (
            "cat <<EOF; [[\nhello\nEOF\na == a ]]\nnext\n",
            ["cat <<EOF; [[\nhello\nEOF\na == a ]]", "next"],
        ),
        # The word after a function definition's `()` starts a command, so a
        # `case` there is one, and its pattern's `)` closes nothing.
        (
            "x=$(f() case a in a) echo A;;\nesac; f)\nnext\n",
            ["x=$(f() case a in a) echo A;;\nesac; f)", "next"],
        ),
    ],
)
def test_script_lines_cuts_where_bash_ends_a_line(script: str, pieces: list[str]) -> None:
    assert [piece for piece, _ in script_lines(script)] == pieces


def test_each_piece_carries_the_offset_its_line_starts_at() -> None:
    script = "cat <<'PY'\nbody\nPY\na \\\n  b\n"

    assert script_lines(script) == (("cat <<'PY'", 0), ("a \\\n  b", 19))


@pytest.mark.parametrize(
    "script",
    ['ok\necho "open\nmore\n', "ok\ncat <<EOF\nnever ends\n", "ok\ncat <<\nnext\n"],
    ids=["an open quote", "a body its delimiter never ends", "a `<<` with no word"],
)
def test_the_rest_of_a_script_that_stops_reading_is_one_unreadable_piece(script: str) -> None:
    """Bash reads an unended body to the end, with a warning; here it is unreadable.

    Where the `<<` is one this reading took for an introducer, taking it as
    bash does would skip the rest of the script without a word.
    """
    (first, _), (rest, _) = script_lines(script)

    assert first == "ok"
    assert shell_words(rest).clauses == ()


@pytest.mark.parametrize(
    ("command", "words"),
    [
        ("python3 tools/x.py \\\n  check", ["python3", "tools/x.py", "check"]),
        # The pair goes from inside a word, and inside double quotes, too.
        ("tools/run\\\nner check", ["tools/runner", "check"]),
        ('echo "a\\\nb"', ["echo", "ab"]),
        # Inside single quotes it is two characters of the word.
        ("echo 'a\\\nb'", ["echo", "a\\\nb"]),
        # A body inside a substitution is skipped; the delimiter is a word.
        (
            'git commit -m "$(cat <<\'EOF\'\nsay "hi"\nEOF\n)"',
            ["git", "commit", "-m", "$(cat <<'EOF'\nsay \"hi\"\nEOF\n)", "cat", "EOF"],
        ),
    ],
)
def test_shell_words_reads_the_newlines_in_a_line_as_bash_does(
    command: str, words: list[str]
) -> None:
    assert _words(command) == words


def test_an_operator_a_continuation_splits_cuts_its_clauses() -> None:
    """`&\\` over `&` is the `&&` the prerequisite rule cuts at, not two `&` (`PL-2JYP`)."""
    reading = shell_words("test -f x &\\\n& grep -q y x")

    assert [clause.text for clause in reading.clauses] == ["test -f x", "grep -q y x"]
    assert reading.refusal is None


@pytest.mark.parametrize(
    ("script", "joined"),
    [
        # A pair bash removes goes, outside quotes, in double quotes and in an
        # unquoted delimiter's body.
        ("echo run\\\nner\n", "echo runner\n"),
        ('echo "a\\\nb"\n', 'echo "ab"\n'),
        ("cat <<EOF\na\\\nb\nEOF\n", "cat <<EOF\nab\nEOF\n"),
        # It stays in single quotes, a comment and a quoted delimiter's body,
        # and under an even run of backslashes.
        ("echo 'a\\\nb'\n", "echo 'a\\\nb'\n"),
        ("# a\\\nb\n", "# a\\\nb\n"),
        ("cat <<'EOF'\na\\\nb\nEOF\n", "cat <<'EOF'\na\\\nb\nEOF\n"),
        ("echo a\\\\\nb\n", "echo a\\\\\nb\n"),
        # From the line that stops reading on, the script is as written.
        ("a\\\nb\necho 'open\nc\\\nd\n", "ab\necho 'open\nc\\\nd\n"),
    ],
)
def test_joined_text_removes_each_backslash_newline_bash_removes(script: str, joined: str) -> None:
    text, origin = joined_text(script)

    assert text == joined
    assert "".join(script[at] for at in origin) == text


def test_a_newline_in_a_substitution_ends_a_command() -> None:
    """Read as a word character, it glued the two commands in the body into one."""
    (body,) = shell_words("v=$(\n  a\n  b\n)").substitutions

    assert body[0].tokens == ("\n", Word("a"), "\n", Word("b"), "\n")


def test_a_field_on_one_line_reads_as_it_did() -> None:
    """No `verify:` holds a newline, so a `<<` there opens nothing to skip."""
    reading = shell_words("cat <<EOF")

    assert [
        token if isinstance(token, str) else token.text for token in reading.clauses[0].tokens
    ] == ["cat", "<<", "EOF"]
    assert reading.refusal == "carries `<<`, which no admitted shape uses"
