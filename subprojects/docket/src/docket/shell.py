"""How a shell command splits: the one reading every rule in docket takes of a `verify:`.

A `verify:` field is a shell line, and several rules ask it questions - whether
it names `docket verify`, which paths it reads, whether it asks the remote,
whether it is one of the shapes `checks.py` admits. They used to ask through
readings of their own, quote regexes and `shlex` beside a lexer, and the
readings disagreed: an apostrophe inside double quotes blanked a real
`bin/docket verify` for one of them, and `a.md|curl` was one word to another
(`PL-P7J7`). So there is one reading, here, and both `checks.py` and
`verify.py` take it. `tools/doc_check.py` takes it too, for the scripts a
workflow's steps run (`PL-CWBJ`), which are many lines where a field is one:
`script_lines` cuts a script where bash ends a line, so a command a backslash,
a quote or a substitution carries past its newline is one piece, and a
here-document's body is the input it is rather than lines of commands
(`PL-Q9LK`).

It stays docket's own rather than the hooks' `.claude/hooks/shell_split.py`
for two reasons: `bin/docket` puts this package alone on the path, and those
words drop the quoting the admitted shapes need (`PL-B5VZ`).
"""

from __future__ import annotations

from dataclasses import dataclass

#: What a word may hold outside quotes with the shell doing nothing to it. `*`
#: and `?` are the exception, admitted in a path to read, where they choose
#: files - item files are named after a title that can change, so
#: `docs/items/PL-K7QX-*.md` outlives a retitle that the full name would not.
PLAIN = frozenset("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_./-+=@%,:")
GLOB = frozenset("*?")
SHELL_OPERATORS = frozenset("|&;<>()")

#: Bash's operators, longest first, so that none is read as two shorter ones:
#: `>|` is a redirection rather than a pipe, and `&>` one rather than a
#: background `&` (Bash Reference Manual, §2 "Definitions"). The hooks read a
#: command by the same table, in `.claude/hooks/shell_split.py`.
OPERATORS = (
    ";;&",
    "<<<",
    "<<-",
    "&>>",
    "&&",
    "||",
    ";;",
    ";&",
    "|&",
    "<<",
    ">>",
    "<&",
    ">&",
    "<>",
    ">|",
    "&>",
    "&",
    "|",
    ";",
    "(",
    ")",
    "<",
    ">",
)


@dataclass(frozen=True)
class Word:
    """One shell word: its text once quotes are removed, and what the shell does to it.

    A command substitution in it stays as written, `$(` or backquote and all,
    the way a double-quoted `$` always has: its body is read as a command of
    its own, into `Reading.substitutions`.
    """

    text: str
    #: Some character of it stood inside quotes or after a backslash.
    quoted: bool = False
    #: An unquoted `*` or `?` stood in it, so the shell may replace it with file names.
    globbed: bool = False
    #: An unquoted `!` stood in it - the negation when it is the whole word.
    bang: bool = False


@dataclass(frozen=True)
class Clause:
    """What runs between two `&&`s: its words and other operators, and its text as written."""

    #: The clause as the command spells it, quotes and all, for a message to name.
    text: str
    #: Its words, as `Word`, and any operator but `&&`, as the string that spells it.
    tokens: tuple[Word | str, ...]
    #: Where each token stands in the command, as `(start, end)` offsets into the
    #: whole command - inside a substitution's body too - one per token.
    spans: tuple[tuple[int, int], ...] = ()


@dataclass(frozen=True)
class Reading:
    """A `verify:` command read once, for every rule in docket that reads one."""

    #: Its clauses, cut at each `&&`; none where the shell could not read it at all.
    clauses: tuple[Clause, ...]
    #: The first thing in it the admitted shapes never use, or `None` where there is none.
    refusal: str | None
    #: The body of every command substitution in it, at any depth, in the order
    #: they open, each cut into clauses as the command is.
    substitutions: tuple[tuple[Clause, ...], ...] = ()

    def every_clause(self) -> tuple[Clause, ...]:
        """Its clauses and every substitution's: each a command the shell runs."""
        return self.clauses + tuple(clause for body in self.substitutions for clause in body)


class _Unreadable(Exception):
    """A command the shell refuses to read, and why."""


class _Lexer:
    """One pass over a command, holding what its substitutions' bodies share with it."""

    def __init__(self, command: str) -> None:
        self.command = command
        self.refusal: str | None = None
        #: Each body read so far, with the offset it opens at, so they sort into order.
        self.bodies: list[tuple[int, tuple[Clause, ...]]] = []
        #: How many substitutions the read stands inside. A newline there ends a
        #: command in the body, and the line the substitution stands on goes on.
        self.nested = 0
        #: Each newline that ends a line, with where the next line starts: past
        #: the bodies of the here-documents the line opened, where it opened any.
        self.breaks: list[tuple[int, int]] = []
        #: Whether a `<<` waits for the word naming its delimiter, and if so
        #: whether it is a `<<-`, which strips tabs; `None` where none waits.
        self.introducer: bool | None = None
        #: The here-documents whose bodies start after the next newline: each
        #: delimiter, and whether its lines' leading tabs are stripped.
        self.pending: list[tuple[str, bool]] = []

    def refuse(self, reason: str) -> None:
        if self.refusal is None:
            self.refusal = reason

    def read(self, index: int, stop: int, closes: bool) -> tuple[tuple[Clause, ...], int]:
        """The clauses from `index`, and the offset just past where they end.

        They end at `stop`, or, where `closes` - the body of a `$(` - at the
        `)` that closes it, which must come first.
        """
        command = self.command
        tokens: list[Word | str] = []
        spans: list[tuple[int, int]] = []
        text: list[str] = []
        begin = -1
        quoted = globbed = bang = False
        depth = 0

        def start() -> None:
            nonlocal begin
            if begin < 0:
                begin = index

        def finish() -> None:
            nonlocal begin, quoted, globbed, bang
            if begin >= 0:
                word = Word("".join(text), quoted, globbed, bang)
                tokens.append(word)
                spans.append((begin, index))
                if self.introducer is not None:  # the word after `<<` names the delimiter
                    self.pending.append((word.text, self.introducer))
                    self.introducer = None
            text.clear()
            begin = -1
            quoted = globbed = bang = False

        while index < stop:
            char = command[index]
            if char in " \t":
                finish()
                index += 1
            elif char == "\n":
                finish()
                if self.introducer is not None:
                    raise _Unreadable("has a `<<` with no word after it")
                self.refuse("carries a newline, which no admitted shape uses")
                tokens.append(char)
                spans.append((index, index + 1))
                resume = self.here_documents(index + 1, stop)
                if not self.nested:
                    self.breaks.append((index, resume))
                index = resume
            elif char == "#" and begin < 0:
                self.refuse("carries an unquoted `#`, which no admitted shape uses")
                end = command.find("\n", index, stop)
                if end < 0:
                    if closes:  # the comment runs to the end, past the `)`
                        raise _Unreadable("has an unclosed command substitution")
                    end = stop
                index = end  # a comment runs to the end of its line
            elif char == "'":
                end = command.find("'", index + 1, stop)
                if end < 0:
                    raise _Unreadable("has an unbalanced quote")
                start()
                text.append(command[index + 1 : end])
                quoted = True
                index = end + 1
            elif char == '"':
                start()
                index = self.double_quoted(index + 1, stop, text)
                quoted = True
            elif char == "\\":
                if index + 1 >= stop:
                    raise _Unreadable("ends in a backslash")
                if command[index + 1] == "\n":  # a continuation: bash removes the pair
                    index += 2
                    continue
                start()
                text.append(command[index + 1])
                quoted = True
                index += 2
            elif char in SHELL_OPERATORS:
                finish()
                if self.introducer is not None:
                    raise _Unreadable("has a `<<` with no word after it")
                operator = next(each for each in OPERATORS if command.startswith(each, index, stop))
                if closes and operator == ")" and not depth:
                    return self.cut(tokens, spans), index + 1
                depth += {"(": 1, ")": -1}.get(operator, 0)
                if operator != "&&":
                    self.refuse(f"carries `{operator}`, which no admitted shape uses")
                if operator in ("<<", "<<-"):
                    self.introducer = operator == "<<-"
                tokens.append(operator)
                spans.append((index, index + len(operator)))
                index += len(operator)
            else:
                if char in GLOB:
                    globbed = True
                elif char == "!":
                    bang = True
                elif char not in PLAIN:
                    shown = repr(char) if char.isspace() else f"`{char}`"
                    self.refuse(f"carries an unquoted {shown}, which no admitted shape uses")
                start()
                end = self.substitution(index, stop)
                text.append(command[index:end])
                index = end
        if closes:
            raise _Unreadable("has an unclosed command substitution")
        finish()
        if self.introducer is not None:
            raise _Unreadable("has a `<<` with no word after it")
        return self.cut(tokens, spans), stop

    def double_quoted(self, index: int, stop: int, text: list[str]) -> int:
        """Read a double-quoted span from just inside its opening quote; the offset past its end.

        A backslash escapes only `"`, a backslash, `$` and a backtick, and a
        `$` or a backtick is refused, since the shell expands it here.
        """
        command = self.command
        while True:
            if index >= stop:
                raise _Unreadable("has an unbalanced quote")
            inner = command[index]
            if inner == '"':
                return index + 1
            if inner in "$`":
                self.refuse(f"has a `{inner}` inside double quotes, where the shell expands it")
                end = self.substitution(index, stop)
                text.append(command[index:end])
                index = end
                continue
            if inner == "\\" and index + 1 < stop and command[index + 1] == "\n":
                index += 2  # a continuation, removed inside double quotes as outside them
                continue
            if inner == "\\" and index + 1 < stop and command[index + 1] in '"\\$`':
                index += 1
                inner = command[index]
            text.append(inner)
            index += 1

    def substitution(self, index: int, stop: int) -> int:
        """The offset past a command substitution opening at `index`, having read its body.

        `index + 1` where none opens there. A `$(` ends at the `)` that closes
        it, read by the same rules as the command, so a `)` inside quotes or a
        subshell does not; a backquote ends at the first backquote no backslash
        escapes (Bash Reference Manual §3.5.4 "Command Substitution").
        """
        command = self.command
        if command.startswith("$(", index, stop):
            self.nested += 1
            clauses, end = self.read(index + 2, stop, closes=True)
            self.nested -= 1
            self.bodies.append((index, clauses))
            return end
        if command[index] == "`":
            close = index + 1
            while close < stop and command[close] != "`":
                close += 2 if command[close] == "\\" else 1
            if close >= stop:
                raise _Unreadable("has an unclosed command substitution")
            self.nested += 1
            clauses, _ = self.read(index + 1, close, closes=False)
            self.nested -= 1
            self.bodies.append((index, clauses))
            return close + 1
        return index + 1

    def here_documents(self, index: int, stop: int) -> int:
        """The offset past the bodies of the here-documents waiting on the newline before `index`.

        Each body runs to the line equal to its delimiter, leading tabs
        stripped for a `<<-`, and that line goes with it (Bash Reference Manual
        §3.6.6 "Here Documents"). Bash reads a body its delimiter never ends to
        the end of the input, with a warning; here that is unreadable instead,
        because the likelier cause is a `<<` this reading took for one - a shift
        inside `(( ))` - and everything after it would go unread unannounced.
        """
        command = self.command
        for delimiter, strip_tabs in self.pending:
            while True:
                if index >= stop:
                    raise _Unreadable(f"has a here-document that `{delimiter}` never ends")
                end = command.find("\n", index, stop)
                end = stop if end < 0 else end
                line = command[index:end]
                index = min(end + 1, stop)
                if (line.lstrip("\t") if strip_tabs else line) == delimiter:
                    break
        self.pending.clear()
        return index

    def cut(self, tokens: list[Word | str], spans: list[tuple[int, int]]) -> tuple[Clause, ...]:
        """The tokens cut into clauses at each `&&`."""
        clauses: list[Clause] = []
        first = 0
        cuts = [at for at, token in enumerate(tokens) if isinstance(token, str) and token == "&&"]
        for cut in [*cuts, len(tokens)]:
            spelled = self.command[spans[first][0] : spans[cut - 1][1]] if cut > first else ""
            clauses.append(Clause(spelled, tuple(tokens[first:cut]), tuple(spans[first:cut])))
            first = cut + 1
        return tuple(clauses)


def shell_words(command: str) -> Reading:
    """The command's clauses and words, and the first thing in it the admitted shapes never use.

    The one reading of a `verify:` command, taken by every rule in docket that
    reads one (`PL-B5VZ`, `PL-P7J7`). `checks.py`'s prerequisite and `-k`
    rules used to cut the command at each `&&` as text, inside quotes too, and
    `verify.py`'s readers found quoted spans with a regex each, which ran from
    one apostrophe to the next across double quotes and the command between.

    A lexer rather than `shlex`, because `shlex` drops the one fact the
    admitted shapes need: whether a character was quoted. `grep -q '$x' f`
    searches for a dollar sign, and `grep -q $x f` searches for whatever the
    shell has in `x`. The rules are bash's (Bash Reference Manual §3.1.2
    "Quoting", §3.1.3 "Comments", §3.5.4 "Command Substitution"): `'...'` is
    literal; in `"..."` a backslash escapes only `"`, a backslash, `$` and a
    backtick; outside quotes it escapes the next character; an operator is the
    longest match in `OPERATORS`; `#` opens a comment only where no word is in
    progress, and it runs to the end of its line; and a `$( )` or a backquote,
    quoted or not, runs a command, so its body is read by these same rules into
    `Reading.substitutions`. A newline is read as bash reads one, though no
    field holds one, because `script_lines` hands this a script's lines: a
    backslash before it removes both, quoted or not, as long as it is not in
    single quotes; unquoted, it ends a command as `;` does, and the bodies of
    the here-documents a `<<` or `<<-` opened before it are skipped to their
    delimiters (§3.1.2.1 "Escape Character", §3.6.6 "Here Documents"). Not
    read, as bash would read them: a command run through `sh -c` or `eval`,
    `$'...'`, which the admitted shapes refuse at its `$`, and a `<<` inside
    `(( ))`, which reads as a here-document here and is unreadable unless a
    line happens to match the word after it.

    Every operator is read rather than stopped at, because a pipe answering
    with another command's status is what the `-k` rule looks for. Every one
    but `&&` is also a refusal where it comes first: a pipe answers with
    another command's status, `||` and `;` replace or discard a failure, a
    redirection or a subshell is a shape nobody has argued for. So are an
    unquoted character outside `PLAIN` and a `$` or backtick inside double
    quotes, where the shell expands it. A command the shell cannot read - an
    unbalanced quote, a trailing backslash, an unclosed substitution, a `<<`
    with no word after it, a here-document its delimiter never ends - has no
    clauses, and its refusal says why unless something earlier already had.
    """
    lexer = _Lexer(command)
    try:
        clauses, _ = lexer.read(0, len(command), closes=False)
    except _Unreadable as unreadable:
        return Reading((), lexer.refusal or str(unreadable))
    bodies = tuple(body for _, body in sorted(lexer.bodies, key=lambda opened: opened[0]))
    return Reading(clauses, lexer.refusal, bodies)


def script_lines(script: str) -> tuple[tuple[str, int], ...]:
    """The script cut where bash ends a line, each piece with the offset it starts at.

    A line ends at a newline that stands outside every quote and substitution
    and that no backslash escapes. So the lines a backslash, a quote or a
    `$( )` carries a command across are one piece, and the bodies of the
    here-documents a line opens come after its newline and belong to no piece,
    since bash reads them as input rather than as commands (Bash Reference
    Manual §3.1.2.1 "Escape Character", §3.6.6 "Here Documents"). A newline
    after `&&` or `|` ends a piece too: the command goes on, and each piece
    still reads whole.

    Each piece is spelled as the script spells it, from where its line starts
    to the newline ending it, so `shell_words` reads it as it stands in the
    script. Its continuations, and the body of any here-document opened inside
    a substitution, are left for that reading to remove: cut out here, a body
    would leave its `<<` to take whatever line came next. Where the script
    stops being readable, everything from the start of that line is one piece,
    which `shell_words` declines in turn.
    """
    lexer = _Lexer(script)
    try:
        lexer.read(0, len(script), closes=False)
    except _Unreadable:
        pass  # the lines before it stand; the rest is the last piece, read as unreadable
    pieces: list[tuple[str, int]] = []
    start = 0
    for end, resume in lexer.breaks:
        pieces.append((script[start:end], start))
        start = resume
    if start < len(script):
        pieces.append((script[start:], start))
    return tuple(pieces)
