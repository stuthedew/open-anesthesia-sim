"""Where bash ends a line of a script and how `shell_words` reads one, held to bash itself.

A workflow step's script reaches bash whole, so `tools/doc_check.py` cuts it with
`shell.script_lines` rather than a line at a time, which read a here-document's
body as commands and declined a command continued past its line (`PL-Q9LK`).
Every hand-written shape below was run through bash 5.2.21 first; where this
reading departs from it, as for a body its delimiter never ends, the departure
is what is pinned.

The last section runs bash: generated scripts go through it and through the
lexer, and every command bash runs must be one the lexer reads, with the words
bash handed it (`PL-C4XY`).
"""

from __future__ import annotations

import bisect
import functools
import re
import shutil
import subprocess
import tempfile
from collections import Counter
from pathlib import Path

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

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


@pytest.mark.parametrize(
    ("script", "pieces"),
    [
        # The word after `function`'s name heads its body, so a `case` there is
        # one, a `((` arithmetic and a `[[` a test.
        (
            "x=$(function f { case a in\n  a) echo in1 ;;\nesac; }; f)\necho b\n",
            ["x=$(function f { case a in\n  a) echo in1 ;;\nesac; }; f)", "echo b"],
        ),
        (
            "function g { ((1 +\n2)) && echo yes; }\ng\n",
            ["function g { ((1 +\n2)) && echo yes; }", "g"],
        ),
        (
            "function h { [[ a == a &&\nb == b ]]; }\nh\n",
            ["function h { [[ a == a &&\nb == b ]]; }", "h"],
        ),
        # The word after `time`'s `-p`, its `--`, or both, is the command it times.
        ("time -p ((1 +\n2))\necho b\n", ["time -p ((1 +\n2))", "echo b"]),
        ("time -- ((1 +\n2))\necho b\n", ["time -- ((1 +\n2))", "echo b"]),
        (
            "time -p -- [[ a == a &&\nb == b ]]\necho b\n",
            ["time -p -- [[ a == a &&\nb == b ]]", "echo b"],
        ),
        (
            "x=$(time -p case a in a) echo in1;;\nesac)\necho b\n",
            ["x=$(time -p case a in a) echo in1;;\nesac)", "echo b"],
        ),
        # The word after `coproc`, or after the name it takes, is the command it runs.
        (
            "x=$(coproc case a in a) echo in1;;\nesac)\necho b\n",
            ["x=$(coproc case a in a) echo in1;;\nesac)", "echo b"],
        ),
        ("coproc named ((1 +\n2))\necho b\n", ["coproc named ((1 +\n2))", "echo b"]),
    ],
)
def test_a_compound_command_after_function_time_p_or_coproc_is_read_whole(
    script: str, pieces: list[str]
) -> None:
    """Bash reads a reserved word past what `function`, `time` and `coproc` take (`PL-0CJC`).

    Read as words, a `case` there let its pattern's `)` close the `$(` around
    it, and a newline inside a `((` or a `[[` ended a line, so one command was
    cut into pieces that each read as complete. Bash 5.2.21 runs each script
    as that command and the line after it.
    """
    assert [piece for piece, _ in script_lines(script)] == pieces


@pytest.mark.parametrize(
    "command",
    ["x=$(time -p case a in a) echo in1;; esac)", "x=$(coproc case a in a) echo in1;; esac)"],
)
def test_a_case_after_time_p_or_coproc_on_one_line_stays_in_its_substitution(command: str) -> None:
    """Its pattern's `)` closes nothing, so the assignment is one word to the last `)`.

    Read as words, the `case` let the `)` after its pattern close the `$(`,
    where bash 5.2.21 runs the `case` whole inside it (`PL-0CJC`).
    """
    assert _words(command)[0] == command


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


def test_a_test_bash_finds_unclosed_is_unreadable() -> None:
    """A `[[` left open at the end of the input, or of its `$( )`, is declined (`PL-0CJC`).

    Read on, it took every line left for the words of its test, where an
    unclosed `$(` is declined and bash 5.2.21 refuses both. Inside a test a
    `)` closes no substitution, so bash refuses one there too, though the
    test's own parentheses are read. The hooks' reading is incomplete, as it
    is for every command bash refuses.
    """
    (first, _), (rest, _) = script_lines("ok\n[[ a &&\nb\n")

    assert first == "ok"
    assert shell_words(rest).clauses == ()
    assert not flat_reading("[[ a &&\nb").complete
    assert shell_words("x=$([[ a ); echo b").clauses == ()
    assert shell_words("x=$([[ ( a ) ]]); echo b").clauses != ()


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


def test_a_nested_backquote_is_read_after_its_escapes_are_removed() -> None:
    """Bash removes a backslash before a backquote, `$` or backslash first (`PL-BHS7`).

    That is how backquotes nest: bash 5.2.21, with `p` printing its arguments
    joined by colons, sets `x` to `bq` for the first command, having run the
    inner `p bq`; read from the raw text, its body was `p` and two words each
    holding an escaped backquote. An escaped `$` expands, two backslashes are
    one, and inside double quotes an escaped `"` quotes, where outside them
    it stays escaped. Each word's span still runs over what the command spells.
    """
    command = "x=`p \\`p bq\\``"
    outer, inner = shell_words(command).substitutions

    assert [token.text for token in outer[0].tokens if isinstance(token, Word)] == ["p", "`p bq`"]
    assert [command[first:last] for first, last in inner[0].spans] == ["p", "bq"]
    assert inner[0].text == "p bq"
    assert flat_reading(command).substituted == (("p", "`p bq`"), ("p", "bq"))
    assert shell_words("x=`p \\$HOME`").substitutions[0][0].tokens[1] == Word("$HOME")
    assert shell_words("x=`p \\\\\\\\`").substitutions[0][0].tokens[1] == Word("\\", quoted=True)
    assert _words('x="`p \\"q r\\"`"')[1:] == ["p", "q r"]
    assert _words('x=`p \\"q r\\"`')[1:] == ["p", '"q', 'r"']
    assert _words("x=`p '\\`p sq\\`'`")[1:] == ["p", "`p sq`"]
    assert joined_text("x=`p \\$a\\\nb`")[0] == "x=`p \\$ab`"


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


# --- held to bash itself (`PL-C4XY`) ------------------------------------------


@functools.cache
def _bash() -> str:
    """The bash the comparison runs, which must read bash 5.2's grammar, as the lexer does."""
    path = shutil.which("bash")
    assert path is not None, "the comparison runs bash, and no bash is on PATH"
    version = subprocess.run(
        [path, "-c", "echo $BASH_VERSION"], capture_output=True, text=True, check=True
    ).stdout.strip()
    major, minor = (int(part) for part in version.split(".")[:2])
    assert (major, minor) >= (5, 2), f"{path} is bash {version}; the comparison needs 5.2 or newer"
    return path


#: What bash runs before each generated script. Every command a script runs is
#: `p`, which writes the words it was handed to descriptor 3, the run's own
#: output: each word ends in a unit separator, a newline in one is written as a
#: group separator, and the command ends in a record separator, all in one
#: write - bash line-buffers its output, and a record a newline split took in
#: another command's from the background. Its standard output goes nowhere, so
#: a substitution of `p` expands to nothing; `set -f` keeps an unquoted `*` a
#: word; an empty `TIMEFORMAT` keeps `time` quiet; and SIGPIPE is ignored,
#: since `time -p` prints to standard error regardless, which a `|&` makes a
#: pipe whose reader may be gone, and the signal ended the commands after it.
PROLOGUE = (
    "exec 3>&1 1>/dev/null\n"
    "trap '' PIPE\n"
    "p() {\n"
    "  local a r=\n"
    "  for a in \"$@\"; do r+=${a//$'\\n'/$'\\035'}$'\\037'; done\n"
    "  printf '%s\\036' \"$r\" >&3\n"
    "}\n"
    "set -f\n"
    "TIMEFORMAT=\n"
)
#: What `time -p` prints to standard error.
TIMED = re.compile(rb"(?m)^(?:real|user|sys) [0-9.]+\n")
#: The path bash hands a command in place of a process substitution.
PROCESS_PATH = re.compile(r"/dev/fd/\d+")


def _bash_runs(script: str) -> Counter[tuple[str, ...]]:
    """Each command bash runs from `script`, as the words it was handed, counted."""
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "script.sh"
        path.write_text(PROLOGUE + script, encoding="utf-8")
        run = subprocess.run(
            [_bash(), "--norc", "--noprofile", str(path)],
            capture_output=True,
            timeout=60,
            check=False,
        )
    assert (run.returncode, TIMED.sub(b"", run.stderr)) == (0, b""), (script, run.stderr)
    return Counter(
        ("p", *(_handed_word(word) for word in record.split("\x1f")[:-1]))
        for record in run.stdout.decode().split("\x1e")[:-1]
    )


def _handed_word(recorded: str) -> str:
    """A word as `p` recorded it, its newlines back and a process substitution's path general."""
    return PROCESS_PATH.sub("/dev/fd/N", recorded.replace("\x1d", "\n"))


#: The operators that end one simple command and start another, once `&&` has cut the clauses.
ENDS = frozenset((";", "\n", "&", "|", "|&", "(", ")", ";;", ";&", ";;&"))
#: The operators whose next word is where the redirection points rather than an argument.
REDIRECTIONS = frozenset(("<", ">", ">>", ">|", "<>", "<&", ">&", "&>", "&>>", "<<", "<<-", "<<<"))
#: The reserved words at a command's head that no command is handed.
RESERVED = frozenset(("if", "then", "fi", "{", "}", "time", "do", "done"))
DESCRIPTOR = re.compile(r"\d+|\{[A-Za-z_]\w*\}")
ASSIGNMENT = re.compile(r"[A-Za-z_]\w*\+?=")
#: A parameter no script sets, so its expansion is nothing.
UNSET = "${unset_value"


def _lexer_runs(script: str) -> Counter[tuple[str, ...]]:
    """Each command `shell_words` reads in `script`, as the words bash would hand it, counted.

    Its clauses and each substitution's are cut into simple commands where an
    operator ends one, and each is read as bash hands it over: a redirection
    and its target, a descriptor written against one, a `case` construct's own
    words, a reserved word or an assignment at its head, and a `for` or `[[`
    command's own words are no command's words; a word that is a substitution
    or a parameter expansion, all of which expand to nothing here, is no word,
    or an empty one in double quotes; and a process substitution is the path
    bash hands over in its place.
    """
    reading = shell_words(script)
    assert reading.clauses, (script, reading.refusal)
    opened = sorted(body[0].spans[0][0] for body in reading.substitutions)
    found: Counter[tuple[str, ...]] = Counter()
    for clause in reading.every_clause():
        command: list[tuple[Word | str, tuple[int, int]]] = []
        for token, span in [*zip(clause.tokens, clause.spans, strict=True), (";", (0, 0))]:
            if isinstance(token, Word) or token not in ENDS:
                command.append((token, span))
                continue
            if words := _handed(script, command, opened):
                found[words] += 1
            command = []
    return found


def _handed(
    script: str, command: list[tuple[Word | str, tuple[int, int]]], opened: list[int]
) -> tuple[str, ...]:
    """The words bash hands the simple command `command` is, or none where it runs none.

    `opened` is where each substitution's body starts, so a word holding one
    is the substitution, whatever its text.
    """
    words: list[str] = []
    timed = False
    skip = False
    for index, (token, (start, end)) in enumerate(command):
        if skip:
            skip = False
            continue
        if not isinstance(token, Word):
            assert token in REDIRECTIONS, (script, token)
            skip = True
            continue
        following = command[index + 1] if index + 1 < len(command) else None
        if (
            following is not None
            and following[0] in REDIRECTIONS
            and following[1][0] == end
            and DESCRIPTOR.fullmatch(script[start:end])
        ):
            continue
        if token.case_syntax:
            continue
        if not words and not token.quoted:
            if token.text in ("for", "[["):
                return ()
            if timed and token.text == "-p":
                continue
            timed = token.text == "time"
            if token.text in RESERVED or ASSIGNMENT.match(token.text):
                continue
        after = bisect.bisect_right(opened, start)
        held = after < len(opened) and opened[after] < end
        if held and token.text.startswith(("<(", ">(")):
            words.append("/dev/fd/N")
        elif held or token.text.startswith(UNSET):
            if token.quoted:
                words.append("")
        else:
            words.append(token.text)
    return tuple(words)


def _lexer_runs_by_piece(script: str) -> Counter[tuple[str, ...]]:
    """`_lexer_runs` a piece of `script_lines` at a time, as doc_check's line readers take one."""
    found: Counter[tuple[str, ...]] = Counter()
    for piece, _ in script_lines(script):
        found += _lexer_runs(piece)
    return found


# The scripts the comparison draws, every command in them `p`. Each helper takes
# the one `draw`, as the front-matter reference's do, which keeps the corpus to
# seconds.

#: What a word may hold unquoted that bash and the lexer both read as itself.
PLAIN = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_./-+=@%,:!^]"
#: Every character that is syntax unquoted, and taken literally after a backslash.
SPECIAL = " \t;&|<>()$`'\"\\#*?[{}~"
#: What a body's random line may hold: no `$`, backquote or backslash, each
#: of which an unquoted body expands, and drawn separately.
BODY = PLAIN + " ;&|<>()'\"#*"
DELIMITERS = ("EOF", "'EOF'", '"EOF"', "E\\OF", "\\EOF", "END_1")
COMMENT = PLAIN + " '\"\\$`()<#;&|"


def _word(draw: st.DrawFn) -> str:
    """A word bash hands over as written once its quotes are removed.

    No `$` stands unescaped before a double quote, where it would open a
    locale string the lexer misreads (`PL-V690`), and a `$'...'` holds no
    backslash, whose escape the lexer keeps as written (`PL-48ZJ`).
    """
    parts: list[str] = []
    for _ in range(draw(st.integers(1, 4))):
        kind = draw(
            st.sampled_from(("plain", "plain", "escaped", "single", "double", "ansi", "join", "#"))
        )
        if kind == "plain":
            parts.append(draw(st.text(PLAIN, min_size=1, max_size=4)))
        elif kind == "escaped":
            parts.append("\\" + draw(st.sampled_from(sorted(SPECIAL + "ab\n"))))
        elif kind == "single":
            parts.append("'" + draw(st.text(PLAIN + ' ;&|<>()$`"\\#*?[{}~\n', max_size=5)) + "'")
        elif kind == "double":
            inside = st.one_of(
                st.text(PLAIN + " ;&|<>()#*?[{}~'\n\t", min_size=1, max_size=3),
                st.sampled_from(('\\"', "\\\\", "\\$", "\\`", "\\a", "\\\n", "\\;")),
            )
            parts.append('"' + "".join(draw(st.lists(inside, max_size=4))) + '"')
        elif kind == "ansi":
            parts.append("$'" + draw(st.text(PLAIN + ' ;&|<>()$`"#*?[{}~', max_size=4)) + "'")
        elif kind == "join":
            parts.append("\\\n")
        else:
            parts.append("#")
    text = "".join(parts)
    # A word of continuations alone is none, and a leading `#` or `~` is syntax.
    if not text.replace("\\\n", "") or text.lstrip("\\\n").startswith(("#", "~")):
        text = "w" + text
    # Bash 5.2.21 reprints a `$( )` before it runs it, and takes a word's last
    # `\&` for the `&` that ends a command: `if p a\&; then` loses its `;`.
    if text.endswith("\\&"):
        text += "w"
    return text


def _backquoted(command: str, quoted: bool) -> str:
    """`command` in backquotes, each character bash removes a backslash before escaped."""
    escaped = command.replace("\\", "\\\\").replace("`", "\\`").replace("$", "\\$")
    return "`" + (escaped.replace('"', '\\"') if quoted else escaped) + "`"


def _substitution(draw: st.DrawFn, depth: int, quoted: bool) -> str:
    """A command substitution, in `$( )` or backquotes, whose output is nothing."""
    if draw(st.booleans()):
        # The space keeps `$(` from opening an arithmetic `$((`, whose body the
        # lexer reads as a command (`PL-3Z8B`). Bash 5.2.21 reprints a `$( )`
        # before it runs it, and drops the first `;` it prints after a
        # here-document's body: `p <<EOF`, the body, then `p a; p b` runs
        # `p a p b`. So only the last command in one opens a here-document.
        return "$( " + _list(draw, depth + 1, lines=True, opens="last") + ")"
    return _backquoted(_simple(draw, depth + 1, bodies=None), quoted)


def _argument(draw: st.DrawFn, depth: int) -> str:
    """A word, or at shallow depth an expansion of one of the kinds bash expands to nothing."""
    if depth >= 2 or draw(st.integers(0, 3)):
        return _word(draw)
    kind = draw(st.sampled_from(("$()", '"$()"', "${}", '"${}"', "${:-}", '"${:-}"', "<()", ">()")))
    quoted = kind.startswith('"')
    if kind in ("<()", ">()"):
        return kind[0] + "( " + _list(draw, depth + 1, lines=False) + " )"
    if ":-" in kind:
        # Inside `${ }` a backquote's quotes are its own, in double quotes or not.
        inner = UNSET + ":-" + _substitution(draw, depth, quoted=False) + "}"
    elif "{" in kind:
        inner = UNSET + "}"
    else:
        inner = _substitution(draw, depth, quoted)
    return f'"{inner}"' if quoted else inner


REDIRECT = (
    "",
    ">/dev/null",
    "2>/dev/null",
    "2>&1",
    ">&2",
    "</dev/null",
    "{v}>/dev/null",
    "&>/dev/null",
)


def _simple(draw: st.DrawFn, depth: int, bodies: list[str] | None) -> str:
    """`p` and its arguments, redirections among them, and a here-document if `bodies` takes one."""
    parts = ["p"]
    for _ in range(draw(st.integers(0, 3))):
        if draw(st.integers(0, 4)) == 0:
            redirect = draw(st.sampled_from((*REDIRECT, "<<<")))
            if redirect == "<<<":
                redirect += _argument(draw, depth)
            if redirect:
                parts.append(redirect)
        else:
            parts.append(_argument(draw, depth))
    if bodies is not None and draw(st.integers(0, 3)) == 0:
        operator, body = _here_document(draw, nested=depth > 0)
        parts.append(operator)
        bodies.append(body)
    return " ".join(parts)


def _here_document(draw: st.DrawFn, nested: bool) -> tuple[str, str]:
    """A `<<` or `<<-` and its delimiter, with the body and delimiter lines that end it.

    A body's substitutions open no here-document of their own, which bash
    5.2.21 refuses where the lexer reads one (`PL-GJKN`). Each runs `p body`,
    or at the top level `p top-body`, which no piece of `script_lines` holds
    (`PL-55R2`).
    """
    spelled = draw(st.sampled_from(DELIMITERS))
    delimiter = re.sub(r"['\"\\]", "", spelled)
    dash = draw(st.booleans())
    quoted = spelled != delimiter
    runs = "p body" if nested else "p top-body"
    lines = draw(
        st.lists(
            st.one_of(
                st.text(BODY, max_size=8),
                st.sampled_from(
                    ("p x", "EOF ", " EOF", "EOFX", "# EOF", "\tEOF", "a\\", "a\\\\", "x)")
                ),
                st.sampled_from((f"$({runs})", f"`{runs}`", f"a $({runs}) b")),
            ),
            max_size=3,
        )
    )
    if dash:
        lines = ["\t" + line for line in lines]
    kept = []
    for line in lines:
        text = line.lstrip("\t") if dash else line
        # A line its delimiter opens ends it, and inside a `$( )` one holding a
        # `)` closes the substitution there too.
        if text == delimiter or (nested and text.startswith(delimiter) and ")" in text):
            continue
        kept.append(line)
    # A continuation joins an unquoted body's next line, so its last may not be one.
    if kept and not quoted and re.search(r"(?<!\\)(\\\\)*\\$", kept[-1]):
        kept[-1] += "z"
    closing = ("\t" if dash else "") + delimiter
    return ("<<-" if dash else "<<") + spelled, "".join(
        line + "\n" for line in kept
    ) + closing + "\n"


def _case(draw: st.DrawFn, depth: int, lines: bool) -> str:
    """A `case` every arm of which runs: `;;&` tries the next, `;&` runs it, `;;` ends."""
    subject = draw(st.sampled_from(("x", '"x"', "'x'", "$( p subject)")))
    matching = ("*", "''") if subject.startswith("$(") else ("*", "x", "?", "[x]", '"x"', "x|*")
    space = "\n" if lines else " "
    arms = []
    count = draw(st.integers(1, 3))
    tried = True
    for index in range(count):
        patterns = draw(st.sampled_from(matching if tried else (*matching, "y", "z|w")))
        if index == 0 and patterns != "*":
            patterns += "|*"
        opening = draw(st.sampled_from(("", "(")))
        # An arm opens no here-document, since a `;` after its body is lost
        # in bash 5.2.21's reprint of the `$( )` it stands in.
        body = _list(draw, depth + 1, lines, opens="none") if draw(st.integers(0, 3)) else ""
        if index == count - 1:
            end = draw(st.sampled_from((";;", "", ";&", ";;&")))
        else:
            end = draw(st.sampled_from((";;&", ";&")))
        tried = end == ";;&"
        if not end:
            # The last arm, which `esac` alone closes: bash reads it as one only
            # where a command could start, after a `;` or a newline (`PL-9NMR`).
            end = ";" if body and not lines else ""
            arms.append(f"{opening}{patterns}) {body}{end}")
        else:
            arms.append(f"{opening}{patterns}) {body}{space}{end}")
    return f"case {subject} in{space}" + space.join(arms) + f"{space}esac"


#: The compound commands a statement may be. No `(( ))`, whose expression the
#: lexer reads as a command in two subshells (`PL-3Z8B`).
COMPOUND = ("group", "subshell", "if", "time", "assign", "array", "case", "for", "test")


def _statement(
    draw: st.DrawFn, depth: int, bodies: list[str] | None, lines: bool, leads: bool
) -> str:
    """A pipeline's element: a simple command, or at shallow depth a compound one.

    `leads` where it opens its pipeline, the one place bash reads `time` as
    the reserved word: after a `|` it is the name of a command.
    """
    kinds: tuple[str, ...] = ("simple",) * 3 + (COMPOUND if leads else COMPOUND[:3] + COMPOUND[4:])
    if depth >= 2:
        kinds = ("simple",)
    elif depth:
        # Bash 5.2.21 misreads an array assignment inside a substitution:
        # `$( a=(\;) )` is a syntax error, and `$( a=(b\<tab>c) )` assigns `b c`.
        kinds = tuple(kind for kind in kinds if kind != "array")
    kind = draw(st.sampled_from(kinds))
    if kind == "simple":
        return _simple(draw, depth, bodies)
    if kind == "group":
        return "{ " + _list(draw, depth + 1, lines=False) + "; }"
    if kind == "subshell":
        return "( " + _list(draw, depth + 1, lines=False) + " )"
    if kind == "if":
        return (
            f"if {_simple(draw, depth + 1, None)}; then {_list(draw, depth + 1, lines=False)}; fi"
        )
    if kind == "time":
        timed = _statement(draw, depth + 1, None, lines=False, leads=False)
        return draw(st.sampled_from(("time ", "time -p "))) + timed
    if kind == "assign":
        return "v=" + _substitution(draw, depth, quoted=False)
    if kind == "array":
        return (
            "a=(" + " ".join(_argument(draw, depth) for _ in range(draw(st.integers(0, 3)))) + ")"
        )
    if kind == "case":
        return _case(draw, depth, lines)
    if kind == "for":
        listed = _substitution(draw, depth, quoted=False) + " 1" if draw(st.booleans()) else "1"
        return f"for _ in {listed}; do {_list(draw, depth + 1, lines=False)}; done"
    # A test of one term, since the lexer reads the `&&`, `||`, parentheses,
    # `<` and `>` inside `[[ ]]` as operators (`PL-X1VN`).
    test = draw(st.sampled_from(("-n x", "x == x", "-z SUB", "SUB == ''")))
    if "SUB" in test:
        test = test.replace("SUB", _substitution(draw, depth, quoted=False))
    # A newline inside `[[ ]]` starts the bodies a `<<` before it opened, so
    # one ends a line only where the bodies it would start are known to be none.
    closing = draw(st.sampled_from((" ]]", "\n]]"))) if bodies == [] else " ]]"
    return f"[[ {test}{closing}"


#: What may stand between two statements on one line, each running both sides.
SEPARATORS = ("; ", " && ", " | ", " & ", " &\\\n& ", " |& ")
#: What may end a line and carry the list on to the next.
LINE_ENDS = ("\n", " &&\n", " |\n")


def _commented(draw: st.DrawFn, ending: str) -> str:
    """`ending`, a comment before its newline now and then."""
    if draw(st.integers(0, 3)):
        return ending
    return ending[:-1] + " #" + draw(st.text(COMMENT, max_size=6)) + "\n"


def _list(
    draw: st.DrawFn,
    depth: int,
    lines: bool,
    bodies: list[str] | None = None,
    leads: bool = True,
    opens: str = "any",
) -> str:
    """One to three statements, each separator one bash runs both sides of.

    Where `lines` holds, a separator may end a line, with the bodies of the
    here-documents opened before it after it. Otherwise any opened go on
    `bodies`, for the caller to place. None opens where `bodies` is None or
    `opens` is "none", and where it is "last" only the last statement opens one.
    """
    own = None if opens == "none" else [] if lines else bodies
    out: list[str] = []
    count = draw(st.integers(1, 3))
    for index in range(count):
        if opens == "last" and index < count - 1:
            out.append(_statement(draw, depth, None, False, leads))
        else:
            out.append(_statement(draw, depth, own, lines, leads))
        if index == count - 1:
            break
        if lines and own:
            separator = "\n"
        else:
            separator = draw(st.sampled_from(SEPARATORS + (LINE_ENDS if lines else ())))
        leads = "|" not in separator
        if separator.endswith("\n"):
            separator = _commented(draw, separator) + "".join(own or ())
            if own:
                own.clear()
        out.append(separator)
    if lines and own:
        out.append("\n" + "".join(own))
    return "".join(out)


@st.composite
def scripts(draw: st.DrawFn) -> str:
    """A script of one to four lines, each a list, its here-documents' bodies after it."""
    out: list[str] = []
    ending = "\n"
    for _ in range(draw(st.integers(1, 4))):
        bodies: list[str] = []
        text = _list(draw, 0, lines=False, bodies=bodies, leads="|" not in ending)
        ending = "\n" if bodies else draw(st.sampled_from((*LINE_ENDS, "\n", ";\n")))
        out.append(text + _commented(draw, ending) + "".join(bodies))
    if ending != "\n" and not ending.startswith(";"):
        out.append("p last\n")
    return "".join(out)


@settings(derandomize=True, database=None, deadline=None, max_examples=300)
@given(scripts())
def test_the_lexer_reads_generated_commands_as_bash_does(script: str) -> None:
    """Each command bash runs from a generated script is one `shell_words` reads, word for word.

    `docket.shell` is what docket's audits and every Bash guard read a command
    with, and no shell library reads both its views as bash does (`PL-JNYL`),
    so bash itself is the reference: each script runs in bash 5.2 or newer,
    every command recording the words it was handed, and the lexer's reading
    of the same script is turned into the commands it says run. The two must
    agree, whole and a piece of `script_lines` at a time but for `p top-body`,
    which no piece holds (`PL-55R2`). Running the script compares what bash
    does; `declare -f` would print bash's reprint of its parse instead, which
    is where the faults the generator steers round live, and would want a
    reader of its own.

    Hypothesis draws the scripts, derandomized, so a red run reproduces
    exactly: words in every quoting, continuations and comments; `$( )`,
    nested backquotes, `${...}` with a default, and process substitutions;
    redirections, descriptors and a `{v}` among them, here-strings, and
    here-documents under every quoting of their delimiter, `<<-` too, inside
    substitutions as well; `;`, `&`, `&&`, `|`, `|&` and an operator a
    continuation splits; and groups, subshells, `if`, `time` and `time -p`,
    assignments, arrays, `for`, `[[ ]]`, and `case` with `;;`, `;&` and `;;&`.
    The same generator, run unseeded over 10,000 scripts on 2026-10-12,
    disagreed with bash on none.

    It leaves out what bash 5.2.21 refuses, or misreads in its reprint of a
    `$( )`, each said where it is drawn, and each form the lexer reads
    differently today, pinned in `KNOWN_DEPARTURES` by the item that will fix
    it.
    """
    expected = _bash_runs(script)

    assert _lexer_runs(script) == expected, script
    del expected[("p", "top-body")]
    assert _lexer_runs_by_piece(script) == expected, script


#: Where the lexer reads a script differently from bash today, each by the item
#: that will make it bash's: the script, what bash runs, and what `shell_words`
#: reads from it whole and a piece of `script_lines` at a time. The generator
#: leaves each form out; the fix deletes its row and lets the generator draw it.
KNOWN_DEPARTURES = [
    pytest.param(
        "p <<EOF\nbody $(p from-a-body) line\nEOF\np after\n",
        {("p",): 1, ("p", "from-a-body"): 1, ("p", "after"): 1},
        {("p",): 1, ("p", "from-a-body"): 1, ("p", "after"): 1},
        {("p",): 1, ("p", "after"): 1},
        id="PL-55R2",
    ),
    pytest.param(
        "p $(( 1 + 2 ))\n",
        {("p", "3"): 1},
        {("p",): 1, ("1", "+", "2"): 1},
        {("p",): 1, ("1", "+", "2"): 1},
        id="PL-3Z8B-expansion",
    ),
    pytest.param(
        "(( 1 + 2 )) && p x\n",
        {("p", "x"): 1},
        {("1", "+", "2"): 1, ("p", "x"): 1},
        {("1", "+", "2"): 1, ("p", "x"): 1},
        id="PL-3Z8B-command",
    ),
    pytest.param(
        'p $"loc"\n', {("p", "loc"): 1}, {("p", "$loc"): 1}, {("p", "$loc"): 1}, id="PL-V690"
    ),
    pytest.param(
        "[[ -n a && -n b ]] && p x\n",
        {("p", "x"): 1},
        {("-n", "b", "]]"): 1, ("p", "x"): 1},
        {("-n", "b", "]]"): 1, ("p", "x"): 1},
        id="PL-X1VN-and",
    ),
    pytest.param(
        "[[ ( -n a ) ]] && p x\n",
        {("p", "x"): 1},
        {("-n", "a"): 1, ("]]",): 1, ("p", "x"): 1},
        {("-n", "a"): 1, ("]]",): 1, ("p", "x"): 1},
        id="PL-X1VN-parentheses",
    ),
    pytest.param(
        "p $'\\x41' $'a\\'b'\n",
        {("p", "A", "a'b"): 1},
        {("p", "\\x41", "a\\'b"): 1},
        {("p", "\\x41", "a\\'b"): 1},
        id="PL-48ZJ",
    ),
]


@pytest.mark.parametrize(("script", "bash", "whole", "pieces"), KNOWN_DEPARTURES)
def test_each_known_departure_from_bash_reads_as_its_row_records(
    script: str,
    bash: dict[tuple[str, ...], int],
    whole: dict[tuple[str, ...], int],
    pieces: dict[tuple[str, ...], int],
) -> None:
    """A form the comparison leaves out still reads as its item says, in bash and in the lexer.

    A row whose reading has changed is fixed or has moved, and either way its
    item, and the generator's exclusion of the form, want revisiting.
    """
    assert _bash_runs(script) == Counter(bash)
    assert _lexer_runs(script) == Counter(whole)
    assert _lexer_runs_by_piece(script) == Counter(pieces)
