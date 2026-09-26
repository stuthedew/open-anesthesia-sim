"""How bash splits a command line, for the three Bash guard hooks to share.

`gate-status-guard.sh`, `floor-interpreter-guard.sh` and `no-prune-guard.sh`
each decide on a command string before it runs, so each has to know where one
command ends and the next begins. Each used to spell that itself - two
`shlex.shlex(punctuation_chars=True)` lexers behind a newline substitution, and
a regex - and each copy read some shape differently from bash. A `)` glued to
the `;` after it hid the separator (`PL-63TT`), a backslash-newline read as one
(`PL-R5RF`), and everything after the first `<<` was dropped rather than only
the heredoc's body (`PL-39LD`). Those are one question answered three times,
which is `PL-PVW2`'s fact, and this module is the one answer the hooks import.

**A small lexer rather than `shlex`, because every one of those fixes needs to
know what is quoted.** `shlex` returns a run of `();<>|&` as one token, and
splitting that run by character would make `>|` a pipe; a backslash-newline is
a continuation only outside single quotes; and a `<<` opens a heredoc only
unquoted. So the rules are bash's own, from the Bash Reference Manual (§2
"Definitions" for the operators, §3.1.2 "Quoting", §3.1.3 "Comments", §3.6.6
"Here Documents") and POSIX.1-2017 XCU §2.3 "Token Recognition" and §2.7.4
"Here-Document", and the shapes the hooks' tests pin were checked against bash
5.2 itself:

- An operator is the longest match in bash's table, so `2>&1` is `2`, `>&`,
  `1`, and `>|`, `&>` and `&>>` never yield a separator.
- `'...'` is literal. In `"..."` a backslash escapes only `$`, a backtick, `"`,
  a backslash and a newline, and a `$( )` inside is read as the command it is,
  so its own quotes and heredocs do not end the word around it - the shape of
  every `git commit -m "$(cat <<'EOF' ... EOF )"`. In `$'...'` a backslash
  escapes the next character, so `\\'` does not close it.
- A backslash-newline outside single quotes is removed, and the line goes on.
- `#` opens a comment only where no word is in progress, and the comment ends
  at its line: under `shlex` it ran to the end of the input, hiding every line
  after it.
- An unquoted newline ends a command as `;` does, except straight after a
  separator or `(`, where bash reads a linebreak: `make check &&` and then
  `tail -5 log` on the next line is one list.
- At each unquoted newline the pending heredocs' bodies are removed, in order.
  A body runs to the line equal to its delimiter - the word after `<<` or
  `<<-` with its quotes removed, leading tabs stripped for `<<-` - or, left
  unterminated, to the end of the input, as bash reads it.
- `$` and the backtick are word characters, and `$(` yields `$` and `(`, so a
  substitution's parentheses reach a walker counting subshells as they did.

**Where a command's words start is answered here too**, by `command_words`,
so no guard can disagree with another about which word is the command. It
drops everything bash reads ahead of a command's name, the reserved words that
open a command included: `do make check` runs `make`, where it once read as a
command named `do` and passed all three guards (`PL-0X0G`). And `commands`
finds every command a string runs, those inside `( )` and `$( )` included, for
a guard that must see one wherever bash would run it. `no-prune-guard.sh` read
that with a regex of its own, which took a `;` inside quotes for a separator
(`PL-WGFY`).

**So is which program a command runs**, by `program_words`, because a program
that runs another is not the one a guard is looking for: `timeout 600 make
check | tail -5` runs `make`, and read from its first word it passed the gate
guard that refuses the same pipe without `timeout` (`PL-TRMN`). `WRAPPERS`
names the programs read past, each by its own option grammar, bare or by path.
Each finds its command on PATH as bash would, which is what lets the floor
guard read `timeout 60 python3` as the bare interpreter it is. `uv run` does
not, so it is the gate guard's to read past, not this module's.

**What it does not read**, none of which a guard here has needed: arithmetic
(`$(( ))` and `(( ))`, where a `<<` shift reads as a heredoc here), the `&&`,
`||`, `<` and `>` inside `[[ ]]`, which read as a separator or a redirection,
the `)` that ends a `case` pattern, a backtick's contents, which split at
spaces as `shlex` split them, the command a `coproc` runs, a wrapper `WRAPPERS`
does not name (`sudo`, `stdbuf`, a `time` run by path), and the string `env -S`
splits, for which `program_words` reads no program at all. A reserved word
opens a command here only at the head of its segment, so `command_words` does
not reach the `make check` in `if (true) then make check; fi` or in `for f do
make check; done`; `commands` reads the first, splitting at its `)`. And a
quoted `if` or `{`, or a `time` after a `|`, reads as the reserved word, where
bash reads a command's name.

A command bash would refuse - an unclosed quote or substitution, a `<<` with no
word after it - is unreadable. `words` and `segments` answer None for it, and
the gate and floor guards fail open on that, as they always have. `commands`
still reads it as far as it can, because bash runs every line before the one it
cannot finish. Standard library only, and it parses at the floor
`tests/unit/test_tools_portability.py` holds `.claude/hooks/` to.
"""

from __future__ import annotations

import re
from typing import NamedTuple


class Operator(str):
    """A token bash reads as an operator, as against a word that spells one.

    `echo ";"` passes the word `;` to `echo`, and only an unquoted `;` ends a
    command, so the two cannot both be plain strings.
    """

    __slots__ = ()


# Bash's control and redirection operators, matched longest first.
OPERATORS = frozenset("; ;; ;& ;;& & && &> &>> | || |& ( ) < << <<- <<< <& <> > >> >& >|".split())
OPERATOR_CHARACTERS = frozenset("&|;()<>")

# The operators that end a command, and the one each is read as: `|&` is a pipe
# that carries stderr too, and `;;`, `;&` and `;;&` end a `case` clause as `;`
# ends a command.
SEPARATORS = {
    ";": ";",
    ";;": ";",
    ";&": ";",
    ";;&": ";",
    "&": "&",
    "&&": "&&",
    "||": "||",
    "|": "|",
    "|&": "|",
}

# A newline straight after one of these is a linebreak, not another separator.
LINEBREAK_AFTER = frozenset(SEPARATORS) | {"("}

# What a backslash escapes inside double quotes; before anything else it is kept.
ESCAPED_IN_DOUBLE_QUOTES = frozenset('$`"\\\n')

# A subshell's `(`, a group's `{` and a negation's `!` open the command after them.
GROUPING = frozenset(("(", "{", "!"))

# The reserved words bash reads with a command after them: `if`, `while` and
# `until` open a test, `then`, `else` and `do` a body, `elif` another test, and
# `time` a pipeline it times (`help if`, `help while`, `help until`, `help for`
# and `help time` in bash 5.2.21). The rest of `compgen -k` opens none: `for`,
# `select`, `case` and `function` are followed by a name or a word, `in` by
# words, and `fi`, `done`, `esac`, `}` and `]]` close what came before.
OPENS_A_COMMAND = frozenset(("if", "then", "elif", "else", "while", "until", "do", "time"))

# The options `time` takes ahead of its pipeline, each at most once and in this
# order: `time -p -- make check` times `make check`.
TIME_OPTIONS = ("-p", "--")

# A leading `NAME=value` sets the command's environment, and is not its name.
ASSIGNMENT = re.compile(r"^[A-Za-z_]\w*=")


class Grammar(NamedTuple):
    """How one wrapper reads the words ahead of the command it runs, as GNU getopt reads them."""

    # Short options whose value is the rest of the word, or else the next word.
    valued: str = ""
    # Short options whose value is only ever the rest of the word.
    optional: str = ""
    # Short options taking no value, which a bundle may run on after.
    flags: str = ""
    # Long options whose value follows an `=`, or else is the next word; each
    # may be abbreviated to any prefix no other long option shares.
    long_valued: tuple[str, ...] = ()
    # Long options taking a value only after an `=`, and those taking none.
    long_other: tuple[str, ...] = ()
    # Options after which no program is read: one that describes a command
    # rather than running it, or one that runs a string this does not split.
    stops: frozenset[str] = frozenset(("help", "version"))
    # The words read between the options and the command: a duration.
    operands: int = 0


# The programs that run a command named after their own options, finding it on
# PATH as bash would, from `timeout --help`, `env --help`, `nice --help` and
# `nohup --help` in coreutils 9.4, `xargs --help` in findutils 4.9.0, and `help
# command` and `help exec` in bash 5.2.21, each spelling run to see which word
# it ran (`PL-TRMN`). Every one stops reading options at its first word that is
# not one, so an option after the command is the command's: `timeout 5 echo -s
# x` prints `-s x`.
WRAPPERS = {
    "timeout": Grammar(
        valued="ks",
        flags="v",
        long_valued=("kill-after", "signal"),
        long_other=("foreground", "preserve-status", "verbose"),
        operands=1,
    ),
    "env": Grammar(
        valued="uCS",
        flags="i0v",
        long_valued=("unset", "chdir", "split-string"),
        long_other=(
            "ignore-environment",
            "null",
            "block-signal",
            "default-signal",
            "ignore-signal",
            "list-signal-handling",
            "debug",
        ),
        stops=frozenset(("help", "version", "S", "split-string")),
    ),
    "nice": Grammar(valued="n", long_valued=("adjustment",)),
    "nohup": Grammar(),
    "xargs": Grammar(
        valued="adEILnPs",
        optional="eil",
        flags="0oprtx",
        long_valued=(
            "arg-file",
            "delimiter",
            "max-lines",
            "max-args",
            "max-procs",
            "max-chars",
            "process-slot-var",
        ),
        long_other=(
            "null",
            "eof",
            "replace",
            "open-tty",
            "interactive",
            "no-run-if-empty",
            "show-limits",
            "verbose",
            "exit",
        ),
    ),
    # `command -v` and `-V` describe the command and run nothing.
    "command": Grammar(flags="p", stops=frozenset(("help", "v", "V"))),
    "exec": Grammar(valued="a", flags="cl"),
}

# `nice`'s older spelling of an adjustment: `nice -5` and `nice --5`.
NICE_ADJUSTMENT = re.compile(r"^-[-+]?\d")


def words(command: str) -> list[str] | None:
    """The tokens bash reads in `command`, or None where bash would refuse it.

    Words come with their quotes removed and operators as `Operator`, with each
    newline that ends a command read as `;` and every comment, continuation and
    heredoc body gone.
    """
    reader = _Reader(command, [], 0, nested=False)
    try:
        reader.read()
    except _Unreadable:
        return None
    return reader.tokens


def segments(command: str) -> list[tuple[list[str], str | None]] | None:
    """`command` cut into its commands, each with the separator that ends it.

    The separator is `;`, `&`, `&&`, `||` or `|` - `|&` read as the pipe it is,
    and a `case` terminator as `;` - and None for the last command. A trailing
    `;` ends nothing and is dropped, while a trailing `&` leaves an empty last
    command, as `make check &` backgrounds the gate. None where `words` is.
    """
    tokens = words(command)
    return None if tokens is None else _cut(tokens)


def command_words(segment: list[str]) -> list[str]:
    """`segment` from its command word on, with what bash reads ahead of it dropped.

    That is any run of grouping and of the reserved words that open a command,
    `time`'s options with it - `then ! time -p make check` runs `make` - and
    then any assignments. Assignments come last because bash reads a reserved
    word only as a command's first word: after `FOO=1`, `if` and `time` are
    the names of programs, which bash 5.2.21 reports it cannot find (`PL-0X0G`).

    Every guard reads the head of a command through this, so none can disagree
    with another about which word is the command - as two readers inside one
    hook once did, and a `set` opening a group went unseen (`PL-1SFZ`).
    """
    rest = list(segment)
    while rest and (rest[0] in GROUPING or rest[0] in OPENS_A_COMMAND):
        if rest.pop(0) == "time":
            for option in TIME_OPTIONS:
                if rest and rest[0] == option:
                    rest.pop(0)
    while rest and ASSIGNMENT.match(rest[0]):
        rest.pop(0)
    return rest


def program_words(segment: list[str]) -> list[str]:
    """`segment` from the program it runs: its command word, or past each wrapper ahead of it.

    `timeout 60 nice -n 5 git fetch --prune` runs `git`, so that is where the
    words start (`PL-TRMN`). Empty where the wrapper runs nothing - `command -v
    git` describes it, a wrapper given no command runs none, and one refusing
    an option it does not know stops there - or runs a string this does not
    read, as `env -S` does.
    """
    rest = command_words(segment)
    while rest and _basename(rest[0]) in WRAPPERS:
        rest = _run_by(rest)
    return rest


def _basename(word: str) -> str:
    return word.rsplit("/", 1)[-1]


def _long_option(grammar: Grammar, written: str) -> str | None:
    """The long option `written` names, whole or as an abbreviation getopt accepts, or None."""
    names = (*grammar.long_valued, *grammar.long_other, "help", "version")
    if written in names:
        return written
    matching = [name for name in names if name.startswith(written)]
    return matching[0] if len(matching) == 1 else None


def _run_by(words: list[str]) -> list[str]:
    """The words of the command the wrapper opening `words` runs, or [] as `program_words` says."""
    name = _basename(words[0])
    grammar = WRAPPERS[name]
    at = 1
    while at < len(words):
        word = words[at]
        if isinstance(word, Operator) or not word.startswith("-") or word == "-":
            break
        at += 1
        if word == "--":
            break
        if name == "nice" and NICE_ADJUSTMENT.match(word):
            continue
        if word.startswith("--"):
            written, equals, _ = word[2:].partition("=")
            option = _long_option(grammar, written)
            if option is None or option in grammar.stops:
                return []
            if option in grammar.long_valued and not equals:
                at += 1
            continue
        for position, letter in enumerate(word[1:], 2):
            if letter in grammar.stops:
                return []
            if letter in grammar.valued:
                # The value is the rest of the word, or the next word if none is left.
                if position == len(word):
                    at += 1
                break
            if letter in grammar.optional:
                break
            if letter not in grammar.flags:
                return []
    if name == "env":
        # A lone `-` is `-i`, and each `NAME=VALUE` sets the command's environment.
        if at < len(words) and words[at] == "-":
            at += 1
        while at < len(words) and "=" in words[at] and not isinstance(words[at], Operator):
            at += 1
    at += grammar.operands
    if at >= len(words) or isinstance(words[at], Operator):
        return []
    return words[at:]


def commands(command: str) -> list[list[str]]:
    """Every command in `command` that bash would run, each read through `program_words`.

    A segment ends only at a separator; a command also starts after each `(`
    or `)` read as an operator, so a subshell, a `$( )`, a `<( )` and the
    command after a `case` pattern each yield their own. The commands in a
    `$( )` inside double quotes are read too: their text stays in the quoted
    word, and they run all the same.

    Never None, unlike `words` and `segments`. Where bash would refuse the
    command, it has still run every line before the one it could not finish,
    so what could be read before that point is returned rather than nothing.
    """
    reader = _Reader(command, [], 0, nested=False)
    try:
        reader.read()
    except _Unreadable:
        pass
    found: list[list[str]] = []
    for tokens in (reader.tokens, *reader.substituted):
        for segment, _ in _cut(tokens):
            piece: list[str] = []
            for token in [*segment, Operator(")")]:
                if isinstance(token, Operator) and token in ("(", ")"):
                    head = program_words(piece)
                    if head:
                        found.append(head)
                    piece = []
                else:
                    piece.append(token)
    return found


def _cut(tokens: list[str]) -> list[tuple[list[str], str | None]]:
    """`tokens` cut at each separator, as `segments` describes."""
    if tokens and isinstance(tokens[-1], Operator) and SEPARATORS.get(tokens[-1]) == ";":
        tokens = tokens[:-1]
    cut: list[tuple[list[str], str | None]] = []
    current: list[str] = []
    for token in tokens:
        if isinstance(token, Operator) and token in SEPARATORS:
            cut.append((current, SEPARATORS[token]))
            current = []
        else:
            current.append(token)
    cut.append((current, None))
    return cut


class _Unreadable(Exception):
    """A command bash would refuse."""


def _kept(text: str, removed: list[tuple[int, int]], start: int, end: int) -> str:
    """`text[start:end]` without the removed spans that lie inside it."""
    parts: list[str] = []
    at = start
    for first, last in sorted(removed):
        if first >= at and last <= end:
            parts.append(text[at:first])
            at = last
    parts.append(text[at:end])
    return "".join(parts)


def _operator_at(text: str, at: int) -> str:
    """The longest of bash's operators starting at `at`, where an operator character stands."""
    for length in (3, 2):
        if text[at : at + length] in OPERATORS:
            return text[at : at + length]
    return text[at]


def _backquote_end(text: str, opening: int) -> int:
    """Where the backquote closing the one at `opening` stands, or -1."""
    at = opening + 1
    while at < len(text):
        if text[at] == "\\":
            at += 2
        elif text[at] == "`":
            return at
        else:
            at += 1
    return -1


class _Reader:
    """One pass over a command list, left to right, the way bash reads it.

    `removed` collects the spans bash discards before it runs anything, and is
    shared with any `$( )` read inside a double-quoted word, whose spans are
    the command's too.
    """

    def __init__(
        self, text: str, removed: list[tuple[int, int]], start: int, *, nested: bool
    ) -> None:
        self.text = text
        self.removed = removed
        self.at = start
        # A `$( )` inside double quotes is read only to find where it ends: it
        # stops at the `)` that closes it, and its words stay in the quoted word.
        self.nested = nested
        self.depth = 0
        self.tokens: list[str] = []
        self.word: list[str] = []
        self.in_word = False
        # The heredocs whose bodies start at the next unquoted newline: each
        # delimiter, and whether `<<-` strips its lines' leading tabs.
        self.pending: list[tuple[str, bool]] = []
        # Whether a `<<` still waiting for its delimiter is a `<<-`, which
        # strips tabs; None where no `<<` is waiting.
        self.introducer: bool | None = None
        # The tokens of each `$( )` read inside double quotes, whose commands
        # run although their text stays in the quoted word.
        self.substituted: list[list[str]] = []

    def read(self) -> int:
        """Read to the end, or past the `)` that closes a nested list; return where it stopped."""
        text = self.text
        while self.at < len(text):
            character = text[self.at]
            following = text[self.at + 1 : self.at + 2]
            if character in " \t":
                self._end_word()
                self.at += 1
            elif character == "\\":
                if following == "\n":
                    self._remove(self.at, self.at + 2)
                else:
                    self.word.append(following or character)
                    self.in_word = True
                self.at += 2
            elif character == "\n":
                self._end_word()
                self._newline()
            elif character == "#" and not self.in_word:
                end = text.find("\n", self.at)
                end = len(text) if end < 0 else end
                self._remove(self.at, end)
                self.at = end
            elif character == "'":
                self._single_quoted()
            elif character == '"':
                self._double_quoted()
            elif character == "$" and following == "'":
                self._ansi_c_quoted()
            elif character in OPERATOR_CHARACTERS:
                self._end_word()
                if self._operator() == ")" and self.nested:
                    if self.depth == 0:
                        return self.at
                    self.depth -= 1
            else:
                self.word.append(character)
                self.in_word = True
                self.at += 1
        self._end_word()
        if self.introducer is not None or self.nested:
            raise _Unreadable
        return self.at

    def _remove(self, start: int, end: int) -> None:
        self.removed.append((start, end))

    def _end_word(self) -> None:
        if not self.in_word:
            return
        word = "".join(self.word)
        self.tokens.append(word)
        self.word.clear()
        self.in_word = False
        if self.introducer is not None:
            self.pending.append((word, self.introducer))
            self.introducer = None

    def _operator(self) -> str:
        if self.introducer is not None:
            raise _Unreadable
        operator = _operator_at(self.text, self.at)
        if operator in ("<<", "<<-"):
            self.introducer = operator == "<<-"
        elif operator == "(" and self.nested:
            self.depth += 1
        self.tokens.append(Operator(operator))
        self.at += len(operator)
        return operator

    def _newline(self) -> None:
        if self.introducer is not None:
            raise _Unreadable
        last = self.tokens[-1] if self.tokens else None
        if last is not None and not (isinstance(last, Operator) and last in LINEBREAK_AFTER):
            self.tokens.append(Operator(";"))
        self.at += 1
        for delimiter, strip_tabs in self.pending:
            self.at = self._body(delimiter, strip_tabs)
        self.pending.clear()

    def _body(self, delimiter: str, strip_tabs: bool) -> int:
        """Remove one heredoc body and its terminator line; return where the next line starts."""
        text = self.text
        line = self.at
        while line < len(text):
            end = text.find("\n", line)
            stop = len(text) if end < 0 else end + 1
            content = text[line:stop] if end < 0 else text[line:end]
            if (content.lstrip("\t") if strip_tabs else content) == delimiter:
                self._remove(self.at, stop)
                return stop
            line = stop
        self._remove(self.at, len(text))
        return len(text)

    def _single_quoted(self) -> None:
        close = self.text.find("'", self.at + 1)
        if close < 0:
            raise _Unreadable
        self.word.append(self.text[self.at + 1 : close])
        self.in_word = True
        self.at = close + 1

    def _ansi_c_quoted(self) -> None:
        text = self.text
        at = self.at + 2
        while at < len(text) and text[at] != "'":
            at += 2 if text[at] == "\\" else 1
        if at >= len(text):
            raise _Unreadable
        # Its escapes are kept as written: no guard reads what they decode to.
        self.word.append(text[self.at + 2 : at])
        self.in_word = True
        self.at = at + 1

    def _double_quoted(self) -> None:
        text = self.text
        at = self.at + 1
        while at < len(text):
            character = text[at]
            following = text[at + 1 : at + 2]
            if character == '"':
                self.in_word = True
                self.at = at + 1
                return
            if character == "\\" and following in ESCAPED_IN_DOUBLE_QUOTES:
                if following == "\n":
                    self._remove(at, at + 2)
                else:
                    self.word.append(following)
                at += 2
            elif character == "$" and following == "(":
                inner = _Reader(text, self.removed, at + 2, nested=True)
                end = inner.read()
                self.substituted += [inner.tokens, *inner.substituted]
                self.word.append(_kept(text, self.removed, at, end))
                at = end
            elif character == "`":
                close = _backquote_end(text, at)
                if close < 0:
                    raise _Unreadable
                self.word.append(text[at : close + 1])
                at = close + 1
            else:
                self.word.append(character)
                at += 1
        raise _Unreadable
