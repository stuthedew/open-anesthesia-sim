"""How a shell command splits: the one reading docket and the guard hooks take of one.

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
a quote, a substitution, a `${...}`, an array assignment or one of bash's
compound commands carries past its newline is one piece, and a here-document's
body is the input it is rather than lines of commands (`PL-Q9LK`, `PL-2JYP`,
`PL-VJPH`). A body starts after the line its `<<` is read on ends, past any
substitution carried across lines (`PL-QSN5`), and a substitution in the body
of a delimiter with no quoted part is a command bash runs (`PL-P95F`).
`tools/fixture_id_check.py` takes `joined_text`, a script as bash reads it once
each backslash-newline it removes is gone (`PL-WG6S`), in a `.sh` file and a
fenced shell sample alike (`PL-HKR5`).

**The guard hooks read a command here too** (`PL-JNYL`). Their
`.claude/hooks/shell_split.py` held a second lexer of the same grammar, and
`#1377` found and fixed the same three bash facts in each; now it takes
`flat_reading`. So one pass decides where a word, a quote, an operator, a
line, a here-document's body and a substitution end, and builds two views of
it. docket's is `Word`s with their quoting and spans, cut into clauses, with
each substitution's body beside them (`PL-B5VZ`). The hooks' is flat tokens,
operators as `Operator` and a redirection's descriptor as `Descriptor`, a
newline read as `;` except after a separator or `(`, an unquoted `$( )`,
`<( )` or `>( )` read inline, and the tokens of one inside quotes, a `${...}`
or backquotes kept apart, in `FlatReading.substituted`.

The two take input that ends early differently, and each chooses: docket
refuses a trailing backslash and a here-document its delimiter never ends,
since a `<<` it took for an introducer would otherwise skip the rest of a
workflow script without a word, while the hooks read the command as `bash -c`
reads the string the harness hands it, an unended body running to the end of
the input and a trailing backslash a backslash. Bash 5.2.21 keeps that
backslash under `bash -c` and drops one it reads from a file (`PL-JNYL`).

It imports nothing, because every guard imports it on every Bash call; its
value classes are plain classes rather than dataclasses for the same reason,
since `dataclasses` and the `inspect` it brings cost each call about 15 ms
(`PL-JNYL`). `tests/unit/test_shell_reader.py` holds a guard's import to
the modules it loads.
"""

#: What a word may hold outside quotes with the shell doing nothing to it. `*`
#: and `?` are the exception, admitted in a path to read, where they choose
#: files - item files are named after a title that can change, so
#: `docs/items/PL-K7QX-*.md` outlives a retitle that the full name would not.
PLAIN = frozenset("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_./-+=@%,:")
GLOB = frozenset("*?")
SHELL_OPERATORS = frozenset("|&;<>()")

#: Bash's operators, each read as the longest that matches, so that none is
#: read as two shorter ones: `>|` is a redirection rather than a pipe, and `&>`
#: one rather than a background `&` (Bash Reference Manual, §2 "Definitions").
#: Every prefix of one is one too, which is what lets `_operator_at` find the
#: longest a character at a time. The one table: the guard hooks read a
#: command through `flat_reading` (`PL-P72R`).
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

#: The operators after which the next word heads a command, where bash reads a
#: reserved word: the control operators and a subshell's `(`. A newline straight
#: after one is a linebreak rather than another `;`, so `make check &&` over
#: `tail -5 log` is one list (POSIX.1-2017 XCU §2.10.2, `linebreak`).
HEADS = frozenset((";", ";;", ";&", ";;&", "&", "&&", "||", "|", "|&", "("))

#: The reserved words bash reads with a command after them: `if`, `while` and
#: `until` open a test, `then`, `else` and `do` a body, `elif` another test,
#: `{` a group, and `!` and `time` a pipeline they negate or time (`help if`,
#: `help while`, `help until`, `help {` and `help time` in bash 5.2.21, and the
#: Bash Reference Manual §3.2.3 "Pipelines" for `!`).
OPENS_A_COMMAND = frozenset(
    ("if", "then", "elif", "else", "while", "until", "do", "{", "!", "time")
)


class _Value:
    """What `dataclass(frozen=True)` gave the classes below, without importing `dataclasses`.

    Equal where their class and their fields are, hashed and shown by their
    fields. Every guard hook imports this module on each Bash call, and
    `dataclasses` with the `inspect` it imports cost that call about 15 ms
    (`PL-JNYL`).
    """

    __slots__ = ()
    _fields: tuple[str, ...] = ()

    def _values(self) -> tuple[object, ...]:
        return tuple(getattr(self, name) for name in self._fields)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, _Value) or type(other) is not type(self):
            return NotImplemented
        return self._values() == other._values()

    def __hash__(self) -> int:
        return hash(self._values())

    def __repr__(self) -> str:
        shown = ", ".join(
            f"{name}={value!r}" for name, value in zip(self._fields, self._values(), strict=True)
        )
        return f"{type(self).__name__}({shown})"


class Word(_Value):
    """One shell word: its text once quotes are removed, and what the shell does to it.

    A command or process substitution in it stays as written, `$(` or backquote
    and all, the way a double-quoted `$` always has: its body is read as a
    command of its own, into `Reading.substitutions`. A compound array
    assignment's `( ... )` stays as written too, bash reading it as one word
    with the name before it (`PL-VJPH`).
    """

    _fields = __slots__ = ("text", "quoted", "globbed", "bang", "case_syntax")

    def __init__(
        self,
        text: str,
        quoted: bool = False,
        globbed: bool = False,
        bang: bool = False,
        case_syntax: bool = False,
    ) -> None:
        self.text = text
        #: Some character of it stood inside quotes or after a backslash.
        self.quoted = quoted
        #: An unquoted `*` or `?` stood in it, so the shell may replace it with file names.
        self.globbed = globbed
        #: An unquoted `!` stood in it - the negation when it is the whole word.
        self.bang = bang
        #: It is a `case` construct's own word - its `case`, its subject, its
        #: `in`, a pattern or its `esac` - which no command the construct runs
        #: is handed (`PL-M3M4`).
        self.case_syntax = case_syntax


class Clause(_Value):
    """What runs between two `&&`s: its words and other operators, and its text as written."""

    _fields = __slots__ = ("text", "tokens", "spans")

    def __init__(
        self, text: str, tokens: tuple[Word | str, ...], spans: tuple[tuple[int, int], ...] = ()
    ) -> None:
        #: The clause as the command spells it, quotes and all, for a message to name.
        self.text = text
        #: Its words, as `Word`, and any operator but `&&`, as the string that spells it.
        self.tokens = tokens
        #: Where each token stands in the command, as `(start, end)` offsets into the
        #: whole command - inside a substitution's body too - one per token.
        self.spans = spans


class Reading(_Value):
    """A `verify:` command read once, for every rule in docket that reads one."""

    _fields = __slots__ = ("clauses", "refusal", "substitutions")

    def __init__(
        self,
        clauses: tuple[Clause, ...],
        refusal: str | None,
        substitutions: tuple[tuple[Clause, ...], ...] = (),
    ) -> None:
        #: Its clauses, cut at each `&&`; none where the shell could not read it at all.
        self.clauses = clauses
        #: The first thing in it the admitted shapes never use, or `None` where there is none.
        self.refusal = refusal
        #: The body of every command and process substitution in it, at any depth,
        #: in the order they open, each cut into clauses as the command is.
        self.substitutions = substitutions

    def every_clause(self) -> tuple[Clause, ...]:
        """Its clauses and every substitution's: each a command the shell runs."""
        return self.clauses + tuple(clause for body in self.substitutions for clause in body)


class Operator(str):
    """A token bash reads as an operator, as against a word that spells one.

    `echo ";"` passes the word `;` to `echo`, and only an unquoted `;` ends a
    command, so the two cannot both be plain strings.
    """

    __slots__ = ()


class Descriptor(str):
    """The descriptor a redirection names ahead of its operator: `2` in `2>&1`, `fd` in `{fd}>x`.

    POSIX calls it IO_NUMBER (XCU §2.10.1), and bash also takes a `{name}` there
    (Bash Reference Manual §3.6 "Redirections"). Spaced from the operator or
    quoted it is an ordinary word, so it cannot be a plain string either.
    """

    __slots__ = ()


class FlatReading(_Value):
    """A command as the guard hooks read it, from the same pass as `Reading`.

    `tokens` is every word, quotes removed, operators as `Operator` and a
    redirection's descriptor as `Descriptor`, with each newline that ends a
    command read as `;` and every comment, continuation and here-document body
    gone. An unquoted `$( )`, `<( )` or `>( )` is read inline, its parentheses
    as operators, so a walk counting subshells meets them as it always has.
    The tokens of a substitution inside double quotes, a `${...}`, backquotes
    or an array assignment are in `substituted`, one list each in the order
    they open, since they run although their text stays in the word.
    """

    _fields = __slots__ = ("tokens", "substituted", "complete")

    def __init__(
        self, tokens: tuple[str, ...], substituted: tuple[tuple[str, ...], ...], complete: bool
    ) -> None:
        self.tokens = tokens
        self.substituted = substituted
        #: False where bash would refuse the command: the tokens are then those
        #: read before the point it could not get past, since bash has still run
        #: every line before the one it cannot finish.
        self.complete = complete


class _Unreadable(Exception):
    """A command the shell refuses to read, and why."""


def _past_continuations(command: str, index: int, stop: int) -> int:
    """The offset of the first character from `index` that no backslash-newline removes."""
    while command.startswith("\\\n", index, stop):
        index += 2
    return index


def _operator_at(command: str, index: int, stop: int) -> tuple[str, int]:
    """The longest operator at `index`, and the offset just past it.

    Read past any backslash-newline between its characters, which bash
    removes before it splits tokens (POSIX.1-2017 XCU §2.2.1), so `&\\` over
    `&` is `&&` and `<<\\` over `-EOF` is `<<-`.
    """
    operator, end = command[index], index + 1
    while True:
        after = _past_continuations(command, end, stop)
        longer = operator + command[after : after + 1]
        if after >= stop or longer not in OPERATORS:
            return operator, end
        operator, end = longer, after + 1


def _arithmetic(command: str, index: int, stop: int) -> bool:
    """Whether the `(` at `index` opens an arithmetic `(( ))` rather than two subshells.

    Bash reads `((` as arithmetic where the `)` closing its second `(` is
    followed at once by another, and as two subshells where it is not: in bash
    5.2.21 `(( x = 3 ))` sets `x` and `((echo a) )` runs `echo` (Bash Reference
    Manual §3.2.5.2 "Conditional Constructs"). Only parentheses are counted to
    find it, past quotes and escapes.
    """
    at = _past_continuations(command, index + 1, stop)
    if not command.startswith("(", at, stop):
        return False
    depth = 0
    at += 1
    while at < stop:
        char = command[at]
        if char == "\\":
            at += 1
        elif char == "'":
            at = command.find("'", at + 1, stop)
            if at < 0:
                return False
        elif char == '"':
            at += 1
            while at < stop and command[at] != '"':
                at += 2 if command[at] == "\\" else 1
        elif char == "(":
            depth += 1
        elif char == ")":
            if not depth:
                return command.startswith(")", at + 1, stop)
            depth -= 1
        at += 1
    return False


def _names_a_descriptor(text: str) -> bool:
    """Whether `text` is what a descriptor written against a redirection is: digits, or `{name}`."""
    if text.isascii() and text.isdecimal():
        return True
    name = text[1:-1]
    return text[:1] == "{" and text[-1:] == "}" and name.isascii() and name.isidentifier()


def _assigns_a_list(text: str) -> bool:
    """Whether a word so far, unquoted, is a name and `=` or `+=`, so a `(` after it opens an array.

    Bash reads `name=(` and `name+=(`, the `(` against the `=`, as a compound
    array assignment (Bash Reference Manual §6.7 "Arrays"); `"a"=(1)` and
    `echo a=(1)` are syntax errors to bash 5.2.21, and a subscripted name a
    runtime one.
    """
    name = text.removesuffix("=").removesuffix("+")
    return text.endswith("=") and name.isascii() and name.isidentifier()


class _Grammar:
    """The little of bash's grammar one read keeps: what a newline or a `)` does where it stands.

    A newline ends a line and a `)` closes a `$(`, except inside the compound
    commands bash opens with a reserved word, which it reads only at the head
    of a command (Bash Reference Manual §3.2.5.2 "Conditional Constructs"). A
    `case` pattern's `)` closes nothing; inside `(( ))` a newline is a space
    and a `<<` a shift; and inside `[[ ]]` a newline ends no line, though the
    here-documents waiting on it start after it, as bash 5.2.21 reads them.
    One per read, since a substitution's body is a list of its own.
    """

    def __init__(self, arithmetic: bool) -> None:
        #: Whether the next word heads a command, where bash reads a reserved word.
        self.head = True
        #: Whether the last operator was a `(`, so that a `)` after it closes
        #: the `()` of a function definition, whose body heads a command.
        self.opened = False
        #: Each `case` open, innermost last, by what it waits for: its `word`,
        #: its `in`, a `pattern` (where `esac` closes it), the rest of one
        #: (`patterns`), or the commands of the `clause` a pattern opened.
        self.cases: list[str] = []
        #: Whether a `[[` waits for its `]]`.
        self.conditional = False
        #: The depth an arithmetic `(( ))` closes at while one is open, or -1
        #: for the body of a `$(( ))`, which the read's own `)` ends.
        self.arithmetic: int | None = -1 if arithmetic else None

    def word(self, text: str, quoted: bool) -> bool:
        """Read one word: the reserved word it is, where bash reads one.

        True where it is a `case` construct's own word rather than one a
        command is handed: the `case`, the subject, the `in`, each pattern and
        the `esac`.
        """
        reserved = "" if quoted else text
        state = self.cases[-1] if self.cases else ""
        head, self.head, self.opened = self.head, False, False
        if self.arithmetic is not None:
            return False
        if state == "word":
            self.cases[-1] = "in"
            return True
        if state == "in":
            self.cases[-1] = "pattern"  # bash refuses any word but `in` here
            return True
        if state == "pattern" and reserved == "esac":
            self.cases.pop()
            return True
        if state in ("pattern", "patterns"):
            self.cases[-1] = "patterns"
            return True
        if self.conditional:
            self.conditional = reserved != "]]"
            return False
        if head and reserved == "case":
            self.cases.append("word")
            return True
        if head and reserved == "esac" and state == "clause":
            self.cases.pop()
            return True
        if head and reserved == "[[":
            self.conditional = True
            return False
        self.head = head and reserved in OPENS_A_COMMAND
        return False

    def pattern(self, operator: str) -> bool:
        """Whether `operator` is a `case` pattern's own `(` or `)`, which neither nests nor closes.

        Read so, it moves the `case` on to the clause or the pattern after it.
        """
        state = self.cases[-1] if self.cases else ""
        if (operator, state) not in ((")", "pattern"), (")", "patterns"), ("(", "pattern")):
            return False
        self.cases[-1] = "clause" if operator == ")" else "patterns"
        self.head, self.opened = operator == ")", False
        return True

    def operator(self, operator: str) -> None:
        """Read one operator a pattern does not own: where the next word stands after it."""
        if self.arithmetic is not None or self.conditional:
            return
        if self.cases and self.cases[-1] == "clause" and operator in (";;", ";&", ";;&"):
            self.cases[-1] = "pattern"
        self.head = operator in HEADS or (operator == ")" and self.opened)
        self.opened = operator == "("


class _Frame:
    """What one reading - the command, or a substitution's body - holds of its own here-documents.

    Each is a delimiter, whether its lines' leading tabs are stripped, and
    whether its body is read in logical lines, as it is where no part of the
    delimiter was quoted.
    """

    def __init__(self, compat: bool) -> None:
        #: Those a `<<` in this reading opened, whose bodies start after its next newline.
        self.pending: list[tuple[str, bool, bool]] = []
        #: Those a substitution inside it still held when its `)` closed it,
        #: which bash reads after this reading's next newline, ahead of its own.
        self.carried: list[tuple[str, bool, bool]] = []
        #: Whether this is the body of a `$( )`, `<( )` or `>( )`, where bash
        #: ends a body at a line that opens with its delimiter and holds a `)`.
        self.compat = compat


class _Lexer:
    """One pass over a command, holding what its substitutions' bodies share with it."""

    def __init__(self, command: str, *, bash_c: bool) -> None:
        self.command = command
        #: Whether input that ends early is read as `bash -c` reads a string - an
        #: unended body running to the end, a trailing backslash a backslash -
        #: or refused as unreadable (`PL-JNYL`).
        self.bash_c = bash_c
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
        #: The reading of the command and of each substitution's body the read
        #: stands inside, innermost last.
        self.frames: list[_Frame] = []
        #: Where each backslash-newline bash removes stands, by its backslash.
        self.joins: list[int] = []
        #: Every other span bash discards before it runs anything - a comment, a
        #: here-document's body - for the hooks' spelling of a substitution.
        self.removed: list[tuple[int, int]] = []
        #: Where reading jumps past the bodies read after a compatibility end,
        #: from the start of the line after the one it ended on.
        self.jumps: dict[int, int] = {}
        #: The hooks' tokens of each substitution read apart from its words.
        self.substituted: list[list[str]] = []

    def refuse(self, reason: str) -> None:
        if self.refusal is None:
            self.refusal = reason

    def read(
        self,
        index: int,
        stop: int,
        closes: bool,
        flat: list[str],
        arithmetic: bool = False,
        backquote: bool = False,
    ) -> tuple[tuple[Clause, ...], int]:
        """The clauses from `index`, and the offset just past where they end.

        They end at `stop`, or, where `closes` - the body of a `$(`, `<(` or
        `>(` - at the `)` that closes it, which must come first. `arithmetic`
        reads the body of a `$(( ))`, where a newline is a space and a `<<` a
        shift, and `backquote` a backquote's, whose unended here-documents bash
        reads as empty rather than carrying them out. The hooks' tokens go to
        `flat` as they are read.
        """
        command = self.command
        frame = _Frame(compat=closes and not arithmetic)
        self.frames.append(frame)
        # A `<<` outside waits for a word outside, not for the body's first.
        outside, self.introducer = self.introducer, None
        tokens: list[Word | str] = []
        spans: list[tuple[int, int]] = []
        text: list[str] = []
        #: The hooks' spelling of the word in progress, which an inline
        #: substitution ends where docket's word goes on past it.
        spelled: list[str] = []
        begin = -1
        spelling = False
        quoted = globbed = bang = False
        depth = 0
        grammar = _Grammar(arithmetic)

        def start() -> None:
            nonlocal begin, spelling
            if begin < 0:
                begin = index
            spelling = True

        def end_spelling(descriptor: bool = False) -> None:
            nonlocal spelling
            if spelling:
                word = "".join(spelled)
                flat.append(Descriptor(word) if descriptor else word)
            spelled.clear()
            spelling = False

        def finish(redirected: bool = False) -> None:
            nonlocal begin, quoted, globbed, bang
            descriptor = False
            if begin >= 0:
                word = "".join(text)
                # Unquoted, against a redirection's operator, and not the
                # delimiter a `<<` waits for, which takes any word.
                descriptor = (
                    redirected
                    and not quoted
                    and self.introducer is None
                    and _names_a_descriptor(word)
                )
                case = grammar.word(word, quoted)
                tokens.append(Word(word, quoted, globbed, bang, case))
                spans.append((begin, index))
                if self.introducer is not None:  # the word after `<<` names the delimiter
                    frame.pending.append((word, self.introducer, not quoted))
                    self.introducer = None
            end_spelling(descriptor)
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
                if grammar.arithmetic is not None:
                    index += 1  # a space inside `(( ))`, where bash ends no line
                    continue
                self.refuse("carries a newline, which no admitted shape uses")
                if grammar.conditional:  # inside `[[ ]]`: the bodies start, and the line goes on
                    index = self.here_documents(index, stop)
                    continue
                tokens.append(char)
                spans.append((index, index + 1))
                if flat and not (isinstance(flat[-1], Operator) and flat[-1] in HEADS):
                    flat.append(Operator(";"))
                resume = self.here_documents(index, stop)
                if not self.nested:
                    self.breaks.append((index, resume))
                grammar.head = True
                index = resume
            elif char == "#" and begin < 0:
                self.refuse("carries an unquoted `#`, which no admitted shape uses")
                end = command.find("\n", index, stop)
                if end < 0:
                    if closes:  # the comment runs to the end, past the `)`
                        raise _Unreadable("has an unclosed command substitution")
                    end = stop
                self.removed.append((index, end))
                index = end  # a comment runs to the end of its line
            elif char == "'":
                end = command.find("'", index + 1, stop)
                if end < 0:
                    raise _Unreadable("has an unbalanced quote")
                start()
                text.append(command[index + 1 : end])
                spelled.append(command[index + 1 : end])
                quoted = True
                index = end + 1
            elif char == '"':
                start()
                index = self.double_quoted(index + 1, stop, text, spelled)
                quoted = True
            elif char == "\\":
                if index + 1 >= stop:
                    if not self.bash_c:
                        raise _Unreadable("ends in a backslash")
                    start()  # `bash -c` keeps a backslash the input ends on
                    text.append(char)
                    spelled.append(char)
                    quoted = True
                    index += 1
                    continue
                if command[index + 1] == "\n":  # a continuation: bash removes the pair
                    self.joins.append(index)
                    index += 2
                    continue
                start()
                text.append(command[index + 1])
                spelled.append(command[index + 1])
                quoted = True
                index += 2
            elif char in "<>" and grammar.arithmetic is None and self.process(index, stop):
                # A process substitution is part of the word it stands in, as
                # bash 5.2.21 prints `a/dev/fd/63b` for `echo a<(true)b`.
                self.refuse(f"carries `{char}`, which no admitted shape uses")
                end_spelling()  # the hooks read it inline, as its own tokens
                if begin < 0:
                    begin = index
                after = _past_continuations(command, index + 1, stop)
                self.joins.extend(range(index + 1, after, 2))
                flat.extend((Operator(char), Operator("(")))
                end = self.substitution_body(index, after + 1, stop, flat)
                text.append(command[index:end])
                index = end
            elif char in SHELL_OPERATORS:
                operator, end = _operator_at(command, index, stop)
                if (
                    operator == "("
                    and begin >= 0
                    and not quoted
                    and grammar.arithmetic is None
                    and not grammar.conditional
                    and _assigns_a_list("".join(text))
                ):
                    self.refuse("carries `(`, which no admitted shape uses")
                    end = self.array(index, stop)
                    text.append(command[index:end])
                    spelled.append(self.kept(index, end))
                    index = end
                    continue
                finish(redirected=operator[0] in "<>" and grammar.arithmetic is None)
                if self.introducer is not None:
                    raise _Unreadable("has a `<<` with no word after it")
                self.joins.extend(
                    at for at in range(index + 1, end) if command.startswith("\\\n", at)
                )
                if not grammar.pattern(operator):  # a pattern's `)` neither nests nor closes
                    if closes and operator == ")" and not depth:
                        flat.append(Operator(operator))
                        self.frames.pop()
                        # Bash reads the bodies still waiting after the line this closes on.
                        self.frames[-1].carried += frame.carried + frame.pending
                        self.introducer = outside
                        return self.cut(tokens, spans), end
                    opens = operator == "(" and grammar.head and grammar.arithmetic is None
                    if opens and _arithmetic(command, index, stop):
                        grammar.arithmetic = depth
                    depth += {"(": 1, ")": -1}.get(operator, 0)
                    if operator == ")" and grammar.arithmetic == depth:
                        grammar.arithmetic = None  # the `))` closing an arithmetic command
                    grammar.operator(operator)
                if operator != "&&":
                    self.refuse(f"carries `{operator}`, which no admitted shape uses")
                if (
                    operator in ("<<", "<<-")
                    and grammar.arithmetic is None
                    and not grammar.conditional
                ):
                    self.introducer = operator == "<<-"
                tokens.append(operator)
                spans.append((index, end))
                flat.append(Operator(operator))
                index = end
            else:
                if char in GLOB:
                    globbed = True
                elif char == "!":
                    bang = True
                elif char not in PLAIN:
                    shown = repr(char) if char.isspace() else f"`{char}`"
                    self.refuse(f"carries an unquoted {shown}, which no admitted shape uses")
                start()
                after = _past_continuations(command, index + 1, stop) if char == "$" else index
                follows = command[after : after + 1] if after < stop else ""
                if char == "$" and follows == "(":
                    # Read inline for the hooks, as `$`, `(`, the body and `)`.
                    self.joins.extend(range(index + 1, after, 2))
                    spelled.append(char)
                    end_spelling()
                    flat.append(Operator("("))
                    end = self.substitution_body(
                        index, after + 1, stop, flat, _arithmetic(command, after, stop)
                    )
                elif char == "$" and follows == "'":
                    # ANSI-C quoting: its escapes kept as written, which no reader decodes.
                    self.joins.extend(range(index + 1, after, 2))
                    close = self.ansi_c_end(after, stop)
                    text.append(command[after + 1 : close])
                    spelled.append(command[after + 1 : close])
                    quoted = True
                    index = close + 1
                    continue
                else:
                    end = self.substitution(index, stop)
                    spelled.append(self.kept(index, end))
                text.append(command[index:end])
                index = end
        if closes:
            raise _Unreadable("has an unclosed command substitution")
        finish()
        if self.introducer is not None:
            raise _Unreadable("has a `<<` with no word after it")
        self.frames.pop()
        unended = frame.carried + frame.pending
        if backquote and unended and not self.bash_c:
            # Bash reads one as empty, with a warning, and carries nothing out.
            raise _Unreadable(f"has a here-document that `{unended[0][0]}` never ends")
        self.introducer = outside
        return self.cut(tokens, spans), stop

    def process(self, index: int, stop: int) -> bool:
        """Whether the `<` or `>` at `index` opens a process substitution.

        It does where a `(` follows it at once, past any backslash-newline,
        and no longer operator starts there: `<<(` is a `<<` (Bash Reference
        Manual §3.5.6 "Process Substitution").
        """
        command = self.command
        operator, _ = _operator_at(command, index, stop)
        after = _past_continuations(command, index + 1, stop)
        return operator == command[index] and command.startswith("(", after, stop)

    def double_quoted(self, index: int, stop: int, text: list[str], spelled: list[str]) -> int:
        """Read a double-quoted span from just inside its opening quote; the offset past its end.

        A backslash escapes only `"`, a backslash, `$` and a backtick, and a
        `$` or a backtick is refused, since the shell expands it here. Each
        character goes to `text` and to `spelled`, the hooks' spelling, which
        holds a substitution less what bash discards inside it.
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
                spelled.append(self.kept(index, end))
                index = end
                continue
            if inner == "\\" and index + 1 < stop and command[index + 1] == "\n":
                self.joins.append(index)
                index += 2  # a continuation, removed inside double quotes as outside them
                continue
            if inner == "\\" and index + 1 < stop and command[index + 1] in '"\\$`':
                index += 1
                inner = command[index]
            text.append(inner)
            spelled.append(inner)
            index += 1

    def substitution(self, index: int, stop: int) -> int:
        """The offset past a command substitution opening at `index`, having read its body.

        `index + 1` where none opens there. A `$(` ends at the `)` that closes
        it, read by the same rules as the command, so a `)` inside quotes, a
        subshell or a `case` pattern does not, and a `$((` bash reads as
        arithmetic is read as `(( ))` is; a backquote ends at the first
        backquote no backslash escapes (Bash Reference Manual §3.5.4 "Command
        Substitution", §3.5.5 "Arithmetic Expansion"). A `${` is read to the
        `}` that closes it, as `parameter` reads one. A backslash-newline after
        the `$` is removed first, as bash removes it before it reads what the
        `$` opens. The hooks' tokens of a body read here go to a list of their
        own in `substituted`, the text staying in the word around it.
        """
        command = self.command
        if command[index] == "`":
            return self.backquote(index, stop)
        if command[index] != "$":
            return index + 1
        after = _past_continuations(command, index + 1, stop)
        if not command.startswith(("(", "{"), after, stop):
            return index + 1
        self.joins.extend(range(index + 1, after, 2))
        if command[after] == "{":
            return self.parameter(after + 1, stop)
        sink: list[str] = []
        self.substituted.append(sink)
        arithmetic = _arithmetic(command, after, stop)
        return self.substitution_body(index, after + 1, stop, sink, arithmetic)

    def substitution_body(
        self, opening: int, index: int, stop: int, flat: list[str], arithmetic: bool = False
    ) -> int:
        """Read the body of the substitution opening at `opening`, from `index`, to its `)`.

        The offset past that `)` is returned.
        """
        self.nested += 1
        clauses, end = self.read(index, stop, closes=True, flat=flat, arithmetic=arithmetic)
        self.nested -= 1
        self.bodies.append((opening, clauses))
        return end

    def backquote(self, index: int, stop: int) -> int:
        """The offset past the backquote closing the one at `index`, having read the command inside.

        Bash ends one at the first backquote no backslash escapes.
        """
        command = self.command
        close = index + 1
        while close < stop and command[close] != "`":
            close += 2 if command[close] == "\\" else 1
        if close >= stop:
            raise _Unreadable("has an unclosed command substitution")
        sink: list[str] = []
        self.substituted.append(sink)
        self.nested += 1
        clauses, _ = self.read(index + 1, close, closes=False, flat=sink, backquote=True)
        self.nested -= 1
        self.bodies.append((index, clauses))
        return close + 1

    def ansi_c_end(self, quote: int, stop: int) -> int:
        """The offset of the quote closing the `$'...'` whose opening quote stands at `quote`.

        A backslash escapes the next character in one, an apostrophe included,
        so `\\'` does not close it (Bash Reference Manual §3.1.2.4 "ANSI-C
        Quoting"). Inside double quotes `$'` is a dollar sign and an
        apostrophe, so only an unquoted one, or one inside a `${...}`, is read
        so (`PL-C45K`).
        """
        command = self.command
        at = quote + 1
        while at < stop and command[at] != "'":
            at += 2 if command[at] == "\\" else 1
        if at >= stop:
            raise _Unreadable("has an unbalanced quote")
        return at

    def parameter(self, index: int, stop: int) -> int:
        """The offset past the `}` closing a `${` whose `{` stands just before `index`.

        Bash ends one at the first `}` not escaped, not quoted and not inside a
        nested expansion or substitution - a `{` with no `$` opens nothing -
        and reads a newline inside it as its text, so the line it stands on
        goes on (Bash Reference Manual §3.5.3 "Shell Parameter Expansion";
        POSIX.1-2017 XCU §2.6.2). Its quotes are skipped, a `$'...'` taking
        escapes, as bash 5.2.21 reads them inside one.
        """
        command = self.command
        while index < stop:
            char = command[index]
            if char == "}":
                return index + 1
            if char == "\\":
                if command.startswith("\n", index + 1, stop):
                    self.joins.append(index)
                index += 2
            elif char == "'":
                end = command.find("'", index + 1, stop)
                if end < 0:
                    raise _Unreadable("has an unbalanced quote")
                index = end + 1
            elif char == '"':
                index = self.double_quoted(index + 1, stop, [], [])
            elif char == "$" and command.startswith(
                "'", after := _past_continuations(command, index + 1, stop), stop
            ):
                self.joins.extend(range(index + 1, after, 2))
                index = self.ansi_c_end(after, stop) + 1
            else:
                index = self.substitution(index, stop)
        raise _Unreadable("has an unclosed parameter expansion")

    def array(self, index: int, stop: int) -> int:
        """The offset past the `)` closing the compound array assignment whose `(` is at `index`.

        Bash reads what stands between as the array's words (Bash Reference
        Manual §6.7 "Arrays"): a newline there is a blank, though the
        here-documents waiting on it start after it, as inside `[[ ]]`; a `#`
        opening a word opens a comment; and any operator but the closing `)`
        is a syntax error, each as bash 5.2.21 reads them, though a `<(` or
        `>(` is the process substitution it is. A substitution in a word is
        read as one in double quotes is, its body a command of its own.
        """
        command = self.command
        at = index + 1
        blank = True
        while at < stop:
            char = command[at]
            if char == ")":
                return at + 1
            if char in " \t":
                blank, at = True, at + 1
                continue
            if char == "\n":
                blank, at = True, self.here_documents(at, stop)
                continue
            if char == "#" and blank:
                end = command.find("\n", at, stop)
                end = stop if end < 0 else end
                self.removed.append((at, end))
                at = end
                continue
            blank = False
            if char in "<>" and self.process(at, stop):
                # A process substitution is a word here too: `a=(<(true) x)` has two.
                after = _past_continuations(command, at + 1, stop)
                self.joins.extend(range(at + 1, after, 2))
                sink: list[str] = []
                self.substituted.append(sink)
                at = self.substitution_body(at, after + 1, stop, sink)
                continue
            if char in SHELL_OPERATORS:
                raise _Unreadable(f"has a `{char}` inside an array assignment, which bash refuses")
            if char == "'":
                end = command.find("'", at + 1, stop)
                if end < 0:
                    raise _Unreadable("has an unbalanced quote")
                at = end + 1
            elif char == '"':
                at = self.double_quoted(at + 1, stop, [], [])
            elif char == "\\":
                if command.startswith("\n", at + 1, stop):
                    self.joins.append(at)
                at += 2
            elif char == "$" and command.startswith(
                "'", after := _past_continuations(command, at + 1, stop), stop
            ):
                self.joins.extend(range(at + 1, after, 2))
                at = self.ansi_c_end(after, stop) + 1
            else:
                at = self.substitution(at, stop)
        raise _Unreadable("has an unclosed array assignment")

    def here_documents(self, newline: int, stop: int) -> int:
        """The offset past the bodies of the here-documents waiting on the newline at `newline`.

        Those a substitution still held when its `)` closed it come first,
        then the reading's own, as bash 5.2.21 reads them: in `cat <<A;
        x=$(cat <<B)`, `B`'s body is the line after it and `A`'s the next. A
        `<<` outside a `$( )` or `<( )` waits for the newline after the line
        it closes on, not for one inside it (POSIX.1-2017 XCU §2.7.4). Each
        body runs to the line equal to its delimiter, leading tabs stripped
        for a `<<-`, and that line goes with it (Bash Reference Manual §3.6.6
        "Here Documents"), as `body` reads it.
        """
        frame = self.frames[-1]
        waiting = frame.carried + frame.pending
        own = len(frame.carried)
        frame.carried, frame.pending = [], []
        index = self.jumps.pop(newline + 1, newline + 1)
        resume: int | None = None
        after_compat = -1
        for at, (delimiter, strip_tabs, joined) in enumerate(waiting):
            compat = frame.compat and at >= own and resume is None
            index, rest = self.body(index, stop, delimiter, strip_tabs, joined, compat)
            if rest is not None:
                resume, after_compat = rest, index
        if resume is None:
            return index
        if index != after_compat:
            # The bodies after the one ended early took the lines after its
            # own, so reading jumps past them once the rest of it is read.
            self.jumps[after_compat] = index
        return resume

    def body(
        self, index: int, stop: int, delimiter: str, strip_tabs: bool, joined: bool, compat: bool
    ) -> tuple[int, int | None]:
        """Read one here-document's body: where the next line starts, and where reading resumes.

        The body starts at `index`. The second is `None` unless `compat` and
        the body ends early: inside a `$( )`, `<( )` or `>( )`, bash 5.2.21
        ends one at a line that opens
        with its delimiter, tabs stripped for a `<<-`, and holds a `)` anywhere
        after it, and reads the rest of that line as the body's commands, so
        `EOF)` closes the substitution and `EOFecho x)` runs `echo x` first.
        It does not end one so at the top level, in a subshell, or for a body
        carried out of its substitution. Bash reads a body its delimiter never
        ends to the end of the input, with a warning; here that is unreadable
        unless the input is read as `bash -c` reads it, so that a `<<` docket
        took for one leaves what follows it declined rather than read as a body
        unannounced. Where no part of the delimiter was quoted, `joined`, bash
        expands the body once it has found where the body ends, and `expanded`
        reads the commands that expansion runs.
        """
        begin = index
        while True:
            if index >= stop:
                if not self.bash_c:
                    raise _Unreadable(f"has a here-document that `{delimiter}` never ends")
                if joined:
                    self.expanded(begin, stop)
                self.removed.append((begin, stop))
                return stop, None
            line, after = self.body_line(index, stop, joined)
            content = line.lstrip("\t") if strip_tabs else line
            if content == delimiter:
                if joined:
                    self.expanded(begin, index)
                self.removed.append((begin, after))
                return after, None
            if compat and content.startswith(delimiter) and ")" in content[len(delimiter) :]:
                rest = self.physical(index, len(line) - len(content) + len(delimiter), joined, stop)
                if joined:
                    self.expanded(begin, index)
                self.removed.append((begin, rest))
                return after, rest
            index = after

    def expanded(self, start: int, end: int) -> None:
        """Read the substitutions in an unquoted here-document's body, from `start` to `end`.

        Bash expands the body of a delimiter no part of which is quoted, so a
        `$( )`, a backquote or a `$( )` inside a `${...}` there runs a command;
        a backslash escapes only `$`, a backquote, a backslash and a newline,
        and a quote is the character it is (POSIX.1-2017 XCU §2.7.4,
        `PL-P95F`). Each such body is read as a command of its own, into
        `Reading.substitutions` and `FlatReading.substituted`. Bash 5.2.21
        expands the body only once its delimiter has ended it, so one the
        delimiter line cuts, or one never closed, fails that expansion with an
        error and the script runs on: it is read as the text it is, and nothing
        reading it began is kept.
        """
        command = self.command
        at = start
        while at < end:
            char = command[at]
            if char == "\\":
                at += 2 if command[at + 1 : at + 2] in ("$", "`", "\\", "\n") else 1
                continue
            if char not in "$`":
                at += 1
                continue
            bodies, substituted, joins = len(self.bodies), len(self.substituted), len(self.joins)
            removed, frames, nested = len(self.removed), len(self.frames), self.nested
            introducer, jumps = self.introducer, dict(self.jumps)
            # Its own reading: a here-document it leaves unended is not carried out.
            self.frames.append(_Frame(compat=False))
            try:
                after = self.substitution(at, end)
            except _Unreadable:
                del self.bodies[bodies:], self.substituted[substituted:], self.joins[joins:]
                del self.removed[removed:], self.frames[frames:]
                self.nested, self.introducer, self.jumps = nested, introducer, jumps
                at += 1
                continue
            self.frames.pop()
            at = after

    def body_line(self, index: int, stop: int, joined: bool) -> tuple[str, int]:
        """The here-document line starting at `index`, and the offset where the next one starts.

        `joined` reads it as bash reads the body of an unquoted delimiter: a
        line whose trailing run of backslashes is odd goes on to the next, less
        that backslash and the newline, since each backslash before it escapes
        the one after, and the joined line is the one compared with the
        delimiter, `<<-` stripping the tabs that open it alone (bash 5.2.21;
        POSIX.1-2017 XCU §2.7.4). dash compares the first physical line
        instead, and bash is followed.
        """
        command = self.command
        pieces: list[str] = []
        while True:
            end = command.find("\n", index, stop)
            if end < 0:
                pieces.append(command[index:stop])
                return "".join(pieces), stop
            piece = command[index:end]
            if not (joined and (len(piece) - len(piece.rstrip("\\"))) % 2):
                pieces.append(piece)
                return "".join(pieces), end + 1
            pieces.append(piece[:-1])
            self.joins.append(end - 1)
            index = end + 1

    def physical(self, index: int, offset: int, joined: bool, stop: int) -> int:
        """Where the character `offset` into the body line starting at `index` stands.

        Only a line `body_line` joined differs from `index + offset`: each of
        its pieces but the last loses the backslash and the newline ending it.
        """
        command = self.command
        while joined:
            end = command.find("\n", index, stop)
            piece = command[index:end] if end >= 0 else ""
            if end < 0 or not (len(piece) - len(piece.rstrip("\\"))) % 2:
                break
            if offset < len(piece) - 1:
                break
            offset -= len(piece) - 1
            index = end + 1
        return index + offset

    def kept(self, start: int, end: int) -> str:
        """The command from `start` to `end` less what bash discards in it: the hooks' spelling."""
        command = self.command
        if end - start < 2:  # no continuation or discarded span fits in one character
            return command[start:end]
        cuts = sorted(
            [(at, at + 2) for at in self.joins if start <= at < end]
            + [(first, last) for first, last in self.removed if start <= first and last <= end]
        )
        parts: list[str] = []
        at = start
        for first, last in cuts:
            if first >= at:
                parts.append(command[at:first])
                at = last
        parts.append(command[at:end])
        return "".join(parts)

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
    "Quoting", §3.1.3 "Comments", §3.5.3 "Shell Parameter Expansion", §3.5.4
    "Command Substitution", §3.5.6 "Process Substitution", §6.7 "Arrays"):
    `'...'` is literal; in `"..."` a backslash escapes only `"`, a backslash,
    `$` and a backtick; in `$'...'` it escapes the next character, an
    apostrophe included; outside quotes it escapes the next character; an
    operator is the longest match in `OPERATORS`, read across any
    backslash-newline inside it; `#` opens a comment only where no word is in
    progress, and it runs to the end of its line; a `${...}` is part of its
    word, to the `}` that closes it; a `$( )`, a `<( )`, a `>( )` or a
    backquote, quoted or not, or inside a `${...}`, runs a command, so its body
    is read by these same rules into `Reading.substitutions`; and `name=(`
    opens an array assignment, one word to its `)`. A newline is read as bash
    reads one, though no field holds one, because `script_lines` hands this a
    script's lines: a backslash before it removes both, quoted or not, as long
    as it is not in single quotes; unquoted, it ends a command as `;` does, and
    the bodies of the here-documents a `<<` or `<<-` opened before it are
    skipped to their delimiters, in logical lines where no part of the
    delimiter is quoted (§3.1.2.1 "Escape Character", §3.6.6 "Here
    Documents"). Bash's compound commands bend that, and `_Grammar` follows
    them: a `case` pattern's `)` closes no `$(`, a newline inside `(( ))` or
    `$(( ))` is a space and a `<<` there a shift, and inside `[[ ]]` or an
    array assignment a newline ends no command, though the bodies waiting on
    it start after it. Not read, as bash would read them: a command run
    through `sh -c` or `eval`. The admitted shapes refuse a `$'...'` at its
    `$`, though it is read to its end (`PL-C45K`).

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
    lexer = _Lexer(command, bash_c=False)
    try:
        clauses, _ = lexer.read(0, len(command), closes=False, flat=[])
    except _Unreadable as unreadable:
        return Reading((), lexer.refusal or str(unreadable))
    bodies = tuple(body for _, body in sorted(lexer.bodies, key=lambda opened: opened[0]))
    return Reading(clauses, lexer.refusal, bodies)


def flat_reading(command: str) -> FlatReading:
    """The command as the guard hooks read it, as `bash -c` reads the string it is handed.

    The same pass as `shell_words`, its tokens laid out as `FlatReading`
    describes, reading input that ends early as bash reads a string rather
    than refusing it: a body its delimiter never ends runs to the end of the
    input, and a trailing backslash is a backslash, where bash 5.2.21 reads
    both with a warning or none (`PL-JNYL`). What bash refuses - an unbalanced
    quote, an unclosed substitution, a `<<` with no word after it - leaves it
    incomplete.
    """
    lexer = _Lexer(command, bash_c=True)
    tokens: list[str] = []
    try:
        lexer.read(0, len(command), closes=False, flat=tokens)
    except _Unreadable:
        complete = False
    else:
        complete = True
    substituted = tuple(tuple(body) for body in lexer.substituted)
    return FlatReading(tuple(tokens), substituted, complete)


def script_lines(script: str) -> tuple[tuple[str, int], ...]:
    """The script cut where bash ends a line, each piece with the offset it starts at.

    A line ends at a newline that stands outside every quote, substitution,
    `${...}` and array assignment, outside an arithmetic `(( ))` and a `[[ ]]`,
    and that no backslash escapes. So the lines any of those carries a command
    across are one piece, a `case` inside a `$( )` included, and the bodies of
    the here-documents a line opens come after its newline and belong to no
    piece, since bash reads them as input rather than as commands (Bash
    Reference Manual §3.1.2.1 "Escape Character", §3.2.5.2 "Conditional
    Constructs", §3.5.6 "Process Substitution", §3.6.6 "Here Documents", §6.7
    "Arrays"). A body a `<<` ahead of a substitution opened starts after the
    line the substitution closes on, as bash reads it (`PL-QSN5`). A newline
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
    lexer = _Lexer(script, bash_c=False)
    try:
        lexer.read(0, len(script), closes=False, flat=[])
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


def joined_text(script: str) -> tuple[str, tuple[int, ...]]:
    """The script less each backslash-newline bash removes, and where each character stood.

    Bash removes the pair before it splits words, so a word one carries
    across lines is one word: `echo PL-K7\\` over `QX` prints `PL-K7QX`. It
    keeps one in single quotes, in a comment and in the body of a
    here-document whose delimiter is quoted, and a line ending in an even run
    of backslashes is not continued (POSIX.1-2017 XCU §2.2.1, §2.3, §2.7.4).
    The offsets give, for each character of the text, where it stands in
    `script`, so a reader can name the line a word starts on. Where the script
    stops being readable, everything from the start of that line is as
    written, as `script_lines` hands that line on.
    """
    lexer = _Lexer(script, bash_c=False)
    joins = lexer.joins
    try:
        lexer.read(0, len(script), closes=False, flat=[])
    except _Unreadable:
        readable = lexer.breaks[-1][1] if lexer.breaks else 0
        joins = [at for at in joins if at < readable]
    removed = {at + step for at in joins for step in (0, 1)}
    kept = tuple(at for at in range(len(script)) if at not in removed)
    return "".join(script[at] for at in kept), kept
