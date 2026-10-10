"""Where bash ends a line of a script, and how `shell_words` reads the newlines inside one.

A workflow step's script reaches bash whole, so `tools/doc_check.py` cuts it with
`shell.script_lines` rather than a line at a time, which read a here-document's
body as commands and declined a command continued past its line (`PL-Q9LK`).
Every shape below was run through bash 5.2.21 first; the one place this reading
departs from it, a body its delimiter never ends, is pinned as the departure.
"""

from __future__ import annotations

import pytest

from docket.shell import Word, flat_reading, joined_text, script_lines, shell_words


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
        # A process substitution carries its line on as a `$( )` does, and an
        # array assignment as a quote does, a comment and all (`PL-VJPH`).
        ("echo <(echo a\n) x\nnext\n", ["echo <(echo a\n) x", "next"]),
        ("files=(\n  a # one\n  b\n)\nnext\n", ["files=(\n  a # one\n  b\n)", "next"]),
        # A body waits for the end of the line its substitution closes on, not
        # for a newline inside it, and one a substitution opens and leaves
        # unended is read after that line, ahead of the line's own (`PL-QSN5`).
        (
            "cat <<EOF; x=$(echo a\necho b); next\nbody\nEOF\nlast\n",
            ["cat <<EOF; x=$(echo a\necho b); next", "last"],
        ),
        ("cat <<A; x=$(cat <<B)\nbody-1\nB\nbody-2\nA\nnext\n", ["cat <<A; x=$(cat <<B)", "next"]),
        # Inside a substitution a line that opens with the delimiter and holds a
        # `)` ends the body, and the rest of it is read; the bodies after it
        # take the lines after its own.
        (
            "git commit -m \"$(cat <<'EOF'\nsay\nEOF)\" && next\nlast\n",
            ["git commit -m \"$(cat <<'EOF'\nsay\nEOF)\" && next", "last"],
        ),
        (
            "x=$(cat <<A <<B\na\nAecho mid)\nb\nB\nnext\n",
            ["x=$(cat <<A <<B\na\nAecho mid)", "next"],
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


def test_an_ansi_c_quoted_string_ends_at_the_quote_bash_ends_it_at() -> None:
    """A backslash escapes the next character in `$'...'`, an apostrophe included (`PL-C45K`).

    Read as a `$` and a single-quoted string, `$'a\\'b'` ended at its second
    apostrophe and the rest of the script was one unreadable piece, where bash
    5.2.21 prints `a'b` and then `next`. Bash keeps a backslash-newline inside
    one, and the admitted shapes still refuse one at its `$`.
    """
    script = "echo $'a\\'b'\necho next\n"

    assert [piece for piece, _ in script_lines(script)] == ["echo $'a\\'b'", "echo next"]
    assert joined_text("echo $'a\\\nb'\n")[0] == "echo $'a\\\nb'\n"
    assert (
        shell_words("echo $'a'").refusal == "carries an unquoted `$`, which no admitted shape uses"
    )


def test_a_substitution_in_an_unquoted_body_is_a_command_it_runs() -> None:
    """Bash expands the body of a delimiter with no quoted part (POSIX.1-2017 XCU §2.7.4).

    So a `$( )` or a backquote there runs, and is read as a command of its own
    (`PL-P95F`); a quoted delimiter's body is text. One the delimiter line cuts
    fails that expansion alone in bash 5.2.21, and the script runs on.
    """
    assert _words("cat <<EOF\n$(make check) `ls`\nEOF\n") == ["cat", "EOF", "make", "check", "ls"]
    assert _words("cat <<'EOF'\n$(make check)\nEOF\n") == ["cat", "EOF"]
    assert _words("cat <<EOF\n$(make\nEOF\nnext\n") == ["cat", "EOF", "next"]


def test_the_hooks_read_input_that_ends_early_as_bash_c_reads_it() -> None:
    """The hooks' reading runs an unended body to the end and keeps a trailing backslash.

    Bash 5.2.21 reads the string `bash -c` is handed so, and the harness hands
    it every Bash call, where docket's own reading refuses both (`PL-JNYL`).
    """
    assert flat_reading("cat <<EOF\nbody").tokens == ("cat", "<<", "EOF", ";")
    assert flat_reading("echo a\\").tokens == ("echo", "a\\")
    assert shell_words("echo a\\").clauses == ()


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
