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

**What it does not read**, none of which a guard here has needed: arithmetic
(`$(( ))` and `(( ))`, where a `<<` shift reads as a heredoc here), the `&&`,
`||`, `<` and `>` inside `[[ ]]`, which read as a separator or a redirection,
the `)` that ends a `case` pattern, and a backtick's contents, which split at
spaces as `shlex` split them.

A command bash would refuse - an unclosed quote or substitution, a `<<` with no
word after it - is unreadable, and every hook fails open on that, as it always
has. Standard library only, and it parses at the floor
`tests/unit/test_tools_portability.py` holds `.claude/hooks/` to.
"""

from __future__ import annotations


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
    if tokens is None:
        return None
    if tokens and isinstance(tokens[-1], Operator) and SEPARATORS.get(tokens[-1]) == ";":
        tokens.pop()
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


def command_text(command: str) -> str:
    """`command` as written, less its continuations, comments and heredoc bodies.

    For a guard that reads the text with its own patterns rather than the
    tokens. It is never None: where bash would refuse the command, the part
    that could be read is cleaned and the rest kept raw, so a guard reading
    this never sees less than the whole command.
    """
    removed: list[tuple[int, int]] = []
    try:
        _Reader(command, removed, 0, nested=False).read()
    except _Unreadable as stop:
        return _kept(command, removed, 0, stop.position) + command[stop.position :]
    return _kept(command, removed, 0, len(command))


class _Unreadable(Exception):
    """A command bash would refuse, and where the construct it could not finish starts."""

    def __init__(self, position: int) -> None:
        super().__init__(position)
        self.position = position


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
        # A `<<` or `<<-` still waiting for its delimiter: where it stands, and
        # whether it strips tabs.
        self.introducer: tuple[int, bool] | None = None

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
        if self.introducer is not None:
            raise _Unreadable(self.introducer[0])
        if self.nested:
            raise _Unreadable(self.at)
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
            self.pending.append((word, self.introducer[1]))
            self.introducer = None

    def _operator(self) -> str:
        if self.introducer is not None:
            raise _Unreadable(self.introducer[0])
        operator = _operator_at(self.text, self.at)
        if operator in ("<<", "<<-"):
            self.introducer = (self.at, operator == "<<-")
        elif operator == "(" and self.nested:
            self.depth += 1
        self.tokens.append(Operator(operator))
        self.at += len(operator)
        return operator

    def _newline(self) -> None:
        if self.introducer is not None:
            raise _Unreadable(self.introducer[0])
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
            raise _Unreadable(self.at)
        self.word.append(self.text[self.at + 1 : close])
        self.in_word = True
        self.at = close + 1

    def _ansi_c_quoted(self) -> None:
        text = self.text
        at = self.at + 2
        while at < len(text) and text[at] != "'":
            at += 2 if text[at] == "\\" else 1
        if at >= len(text):
            raise _Unreadable(self.at)
        # Its escapes are kept as written: no guard reads what they decode to.
        self.word.append(text[self.at + 2 : at])
        self.in_word = True
        self.at = at + 1

    def _double_quoted(self) -> None:
        text = self.text
        opening = self.at
        at = opening + 1
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
                try:
                    end = _Reader(text, self.removed, at + 2, nested=True).read()
                except _Unreadable:
                    raise _Unreadable(opening) from None
                self.word.append(_kept(text, self.removed, at, end))
                at = end
            elif character == "`":
                close = _backquote_end(text, at)
                if close < 0:
                    raise _Unreadable(opening)
                self.word.append(text[at : close + 1])
                at = close + 1
            else:
                self.word.append(character)
                at += 1
        raise _Unreadable(opening)
