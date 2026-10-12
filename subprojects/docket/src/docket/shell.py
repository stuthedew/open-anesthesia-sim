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
of a delimiter with no quoted part is a command bash runs (`PL-P95F`), so it
is a piece of its own (`PL-55R2`).
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

#: The reserved words bash reads more words after before the command they lead,
#: so that the command's head is a word further on: `time` its options, `coproc`
#: the name it may take, and `function` the name it must (Bash Reference Manual
#: §3.2.3 "Pipelines", §3.2.6 "Coprocesses", §3.3 "Shell Functions").
LEADS = frozenset(("time", "coproc", "function"))

#: The tests of a conditional expression that take one operand, and those that
#: take two, an unquoted word each; bash reads `<` and `>` there as the two
#: string comparisons (`test_unop` and `test_binop` in bash 5.2.21's test.c,
#: each run through `bash -n`; Bash Reference Manual §6.4 "Bash Conditional
#: Expressions").
UNARY_TESTS = frozenset(f"-{letter}" for letter in "abcdefghknoprstuvwxzGLNORS")
BINARY_TESTS = frozenset(
    ("=", "==", "!=", "=~", "-eq", "-ne", "-lt", "-le", "-gt", "-ge", "-nt", "-ot", "-ef")
)
#: What the word after a binary test is read as: a pattern, whose extglob
#: groups bash reads as pairs, or a regular expression, whose `(` opens a pair
#: and whose `|` is part of it (`PST_EXTPAT` and `PST_REGEXP` in bash 5.2.21's
#: parse.y, `PL-X1VN`).
READS_AFTER = {"==": "pattern", "=": "pattern", "!=": "pattern", "=~": "regex"}


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

    Its text is what bash reads in the C locale, where a `$"..."` locale
    string is the double-quoted string it holds, untranslated (`PL-V690`),
    and a `$'...'` has its escapes replaced as bash replaces them there
    (`PL-48ZJ`).
    A command or process substitution in it stays as written, `$(` or backquote
    and all, the way a double-quoted `$` always has: its body is read as a
    command of its own, into `Reading.substitutions`. A compound array
    assignment's `( ... )` stays as written too, bash reading it as one word
    with the name before it (`PL-VJPH`), and so does arithmetic: a `$(( ))`
    in a word, and an arithmetic command or an arithmetic `for`'s `(( ))` as
    a word of its own, none of which runs a command, though a substitution
    inside one does (`PL-3Z8B`). Inside `[[ ]]` an `&&`, `||`, `(`, `)`, `<`
    or `>` is a word of the conditional, which no command runs and none
    redirects, and a regular expression or a pattern's groups are part of
    their word (`PL-X1VN`).
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

    `tokens` is every word, its quotes removed and a `$'...'`'s escapes
    replaced as in `Word.text`, operators as `Operator` and a redirection's
    descriptor as `Descriptor`, with each newline that ends a command read as
    `;` and every comment, continuation and here-document body gone. An
    unquoted `$( )`, `<( )` or `>( )` is read inline, its parentheses as
    operators, so a walk counting subshells meets them as it always has,
    while arithmetic is the one plain token `Word.text` is (`PL-3Z8B`), and
    a conditional's own operators are plain tokens too (`PL-X1VN`).
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


class _Cut(Exception):
    """A substitution an expanded here-document body runs, which bash cuts short and runs nothing.

    `after` is where the expansion goes on, as `_Lexer.slipped` reads it (`PL-54MD`).
    """

    def __init__(self, after: int) -> None:
        super().__init__(after)
        self.after = after


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


#: The escapes a `$'...'` replaces with one byte each, as bash 5.2.21's
#: `ansicstr` does: the control characters, `\E` the same escape as `\e`, and
#: four characters that stand for themselves.
ANSI_C_ESCAPES = {
    bytes([escape]): bytes([byte])
    for escape, byte in zip(b"abeEfnrtv\\'\"?", b"\a\b\x1b\x1b\f\n\r\t\v\\'\"?", strict=True)
}


def _digits(data: bytes, at: int, most: int, base: int) -> tuple[int, int]:
    """The value of up to `most` digits in `base` from `at`, or 0 for none, and where they end."""
    digits = b"01234567" if base == 8 else b"0123456789abcdefABCDEF"
    end = at
    while end < len(data) and end - at < most and data[end] in digits:
        end += 1
    return (int(data[at:end], base) if end > at else 0), end


def _ansi_c(raw: str) -> str:
    """The text of the `$'...'` holding `raw`, its escapes replaced as bash replaces them.

    Bash 5.2.21's `ansicstr` works on bytes, and so does this, in the C
    locale, measured under `LC_ALL=C` (Bash Reference Manual §3.1.2.4
    "ANSI-C Quoting", `PL-48ZJ`). `\\NNN` takes one to three octal digits
    and `\\xHH` one or two hex digits, and `\\x{...}` every hex digit and an
    optional `}`, each masked to a byte. `\\u` and `\\U` take up to four and
    eight hex digits: at or below 0x7f the value is its character, and above
    it bash writes the escape back, `\\u%04X` below 0x10000 and `\\U%08X`
    below 0x80000000, or nothing at all. `\\cX` is `X` masked with 0x1f, or
    0x7f for `?`; `\\c\\\\` takes both backslashes, and a multibyte `X` gives
    up its first byte alone. Any other escape - `\\8`, `\\q`, a `\\x`, `\\u`
    or `\\U` with no digit, a trailing `\\c` - keeps its backslash. A NUL
    ends the text, which is decoded with `surrogateescape`, so a byte that
    is no UTF-8 stays the byte it was.
    """
    try:
        data = raw.encode("utf-8", "surrogateescape")
    except UnicodeEncodeError:  # a lone surrogate no byte stands for, in no command bash is handed
        data = raw.encode("utf-8", "surrogatepass")
    out = bytearray()
    at = 0
    while at < len(data):
        if data[at] != ord("\\") or at + 1 == len(data):
            out.append(data[at])
            at += 1
            continue
        escape = data[at + 1 : at + 2]
        at += 2
        if escape in ANSI_C_ESCAPES:
            out += ANSI_C_ESCAPES[escape]
        elif escape in b"01234567":
            value, at = _digits(data, at - 1, 3, 8)
            out.append(value & 0xFF)
        elif escape == b"x" and data.startswith(b"{", at):
            value, at = _digits(data, at + 1, len(data), 16)
            if data.startswith(b"}", at):
                at += 1
            out.append(value & 0xFF)
        elif escape in (b"x", b"u", b"U"):
            value, end = _digits(data, at, {b"x": 2, b"u": 4, b"U": 8}[escape], 16)
            if end == at:
                out += b"\\" + escape
            elif value <= 0x7F or escape == b"x":
                out.append(value)
            elif value < 0x10000:
                out += b"\\u%04X" % value
            elif value < 0x80000000:
                out += b"\\U%08X" % value
            at = end
        elif escape == b"c" and at < len(data):
            control = data[at]
            at += 1
            if control == ord("\\") and data.startswith(b"\\", at):
                at += 1
            # Upper-casing a letter first, as bash does, changes no bit the mask keeps.
            out.append(0x7F if control == ord("?") else control & 0x1F)
        else:
            out += b"\\" + escape
    return bytes(out).split(b"\0", 1)[0].decode("utf-8", "surrogateescape")


def _arithmetic(command: str, index: int, stop: int) -> bool:
    """Whether the `(` at `index` opens an arithmetic `(( ))` rather than two subshells.

    Bash reads `((` as arithmetic where the `)` closing its second `(` is
    followed at once by another, and as two subshells where it is not: in bash
    5.2.21 `(( x = 3 ))` sets `x` and `((echo a) )` runs `echo` (Bash Reference
    Manual §3.2.5.2 "Conditional Constructs"). The `)` is found as
    `_Lexer.matched` finds it, by a reading of its own that the command's
    reading never sees, so a comment or a `case` pattern inside a
    substitution there moves it no more than it moves bash's.
    """
    second = _past_continuations(command, index + 1, stop)
    if not command.startswith("(", second, stop):
        return False
    trial = _Lexer(command, bash_c=True)
    trial.frames.append(_Frame(compat=False))
    try:
        close = trial.matched(second, stop)
    except _Unreadable:
        return False  # what bash refuses here, the command's own reading refuses in turn
    return command.startswith(")", close, stop)


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
    `case` pattern's `)` closes nothing, and inside `[[ ]]` a newline ends no
    line, though the here-documents waiting on it start after it, as bash
    5.2.21 reads them. An arithmetic `(( ))` is one word, which `_Lexer`
    reads whole where a head or a `for` opens one (`PL-3Z8B`). Inside `[[ ]]`
    this reads the conditional's own grammar, as `condition` describes, and
    refuses what bash refuses there (`PL-X1VN`).
    A head is where bash 5.2.21 reads a reserved word (`reserved_word_acceptable`
    in its parse.y), and this takes one after a control operator or a newline,
    after a word in `OPENS_A_COMMAND`, after a function definition's `()`, and
    past what a word in `LEADS` takes before its command - `time`'s `-p` and
    then `--`, the name after `function`, and the one `coproc` may take
    (`PL-0CJC`). Not yet after a closing word bash also names there, such as
    `fi` or `]]` (`PL-9NMR`). One per read, since a substitution's body is a
    list of its own.
    """

    def __init__(self) -> None:
        #: Whether the next word heads a command, where bash reads a reserved word.
        self.head = True
        #: Whether the last word was a `for` read at a head, after which a `((`
        #: opens the arithmetic `for`'s expressions (§3.2.5.1 "Looping Constructs").
        self.counting = False
        #: The word in `LEADS` the last word was, read at a head, or `time -p`
        #: once the `-p` after a `time` is read: what bash may still read
        #: before the command it leads.
        self.leading = ""
        #: Whether the last operator was a `(`, so that a `)` after it closes
        #: the `()` of a function definition, whose body heads a command.
        self.opened = False
        #: Each `case` open, innermost last, by what it waits for: its `word`,
        #: its `in`, a `pattern` (where `esac` closes it), the rest of one
        #: (`patterns`), or the commands of the `clause` a pattern opened.
        self.cases: list[str] = []
        #: What an open `[[` waits for next, or "" where none is open: a `term`,
        #: the `operand` of a unary test, the binary test after a term's first
        #: word (`binop`), the word after one - an `operand`, a `pattern` or a
        #: `regex` - or, once a term is whole, what `joined` it to the next.
        self.conditional = ""
        #: How many of the open `[[`'s groups wait for their `)`.
        self.groups = 0

    def word(self, text: str, quoted: bool) -> bool:
        """Read one word: the reserved word it is, where bash reads one.

        True where it is a `case` construct's own word rather than one a
        command is handed: the `case`, the subject, the `in`, each pattern and
        the `esac`.
        """
        reserved = "" if quoted else text
        state = self.cases[-1] if self.cases else ""
        head, self.head, self.opened, self.counting = self.head, False, False, False
        leading, self.leading = self.leading, ""
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
            self.condition(reserved, operator=False)
            return False
        if head and reserved == "case":
            self.cases.append("word")
            return True
        if head and reserved == "esac" and state == "clause":
            self.cases.pop()
            return True
        if head and reserved == "[[":
            self.conditional, self.groups = "term", 0
            return False
        if leading == "time" and reserved == "-p":
            # bash reads `-p` straight after `time`, and `--` after either, as
            # its options (parse.y's `special_case_tokens`).
            self.head, self.leading = True, "time -p"
        elif leading in ("time", "time -p") and reserved == "--":
            self.head = True
        elif leading == "function" or (leading == "coproc" and reserved not in ("for", "select")):
            # The word after the name heads the body `function` defines or the
            # command `coproc` runs; a `for` or `select` there is that command.
            self.head = True
        elif head and reserved in LEADS:
            self.head, self.leading = reserved != "function", reserved
        else:
            self.head = head and reserved in OPENS_A_COMMAND
            self.counting = head and reserved == "for"
        return False

    def pattern(self, operator: str) -> bool:
        """Whether `operator` is a `case` pattern's own `(` or `)`, which neither nests nor closes.

        Read so, it moves the `case` on to the clause or the pattern after it.
        """
        state = self.cases[-1] if self.cases else ""
        if (operator, state) not in ((")", "pattern"), (")", "patterns"), ("(", "pattern")):
            return False
        self.cases[-1] = "clause" if operator == ")" else "patterns"
        self.head, self.opened, self.leading = operator == ")", False, ""
        return True

    def operator(self, operator: str) -> None:
        """Read one operator a pattern does not own: where the next word stands after it."""
        self.leading, self.counting = "", False
        if self.cases and self.cases[-1] == "clause" and operator in (";;", ";&", ";;&"):
            self.cases[-1] = "pattern"
        self.head = operator in HEADS or (operator == ")" and self.opened)
        self.opened = operator == "("

    def condition(self, token: str, operator: bool) -> None:
        """Read one token of an open `[[ ]]`, unreadable where bash refuses it there.

        `token` is a word's text, "" for a quoted one, which none of the
        conditional's own words is, or, where `operator`, the operator or the
        newline read. As bash 5.2.21's `cond_term` reads them, a term opens
        with any `!` and `(`, and is a unary test and its operand, a word, the
        binary test and the word after it, or a word alone; `&&` and `||` join
        two terms, a `)` closes a group, and `]]` the conditional where no
        group is open. A newline stands only before a term or after one, and
        every other operator nowhere (Bash Reference Manual §3.2.5.2
        "Conditional Constructs", `PL-X1VN`).
        """
        expects = self.conditional
        closing = not operator and token == "]]"
        if operator and token == "\n":
            accepted = expects in ("term", "joined")
        elif expects in ("operand", "pattern", "regex"):
            accepted, self.conditional = not (operator or closing), "joined"
        elif expects == "term":
            accepted = not closing and (not operator or token == "(")
            if operator:
                self.groups += 1
            elif token != "!":
                self.conditional = "operand" if token in UNARY_TESTS else "binop"
        elif expects == "binop" and (token in ("<", ">") if operator else token in BINARY_TESTS):
            accepted, self.conditional = True, READS_AFTER.get(token, "operand")
        elif operator and token in ("&&", "||"):
            accepted, self.conditional = True, "term"
        elif operator and token == ")":
            accepted, self.conditional = self.groups > 0, "joined"
            self.groups -= 1
        else:
            accepted, self.conditional = closing and not self.groups, ""
        if not accepted:
            shown = "a newline" if token == "\n" else f"`{token}`" if token else "a quoted word"
            raise _Unreadable(f"has {shown} where its `[[ ]]` cannot take it")


class _Frame:
    """What one reading - the command, or a substitution's body - holds of its own here-documents.

    Each is a delimiter, whether its lines' leading tabs are stripped, and
    whether its body is read in logical lines, as it is where no part of the
    delimiter was quoted.
    """

    def __init__(self, compat: bool, expansion: bool = False) -> None:
        #: Those a `<<` in this reading opened, whose bodies start after its next newline.
        self.pending: list[tuple[str, bool, bool]] = []
        #: Those a substitution inside it still held when its `)` closed it,
        #: which bash reads after this reading's next newline, ahead of its own.
        self.carried: list[tuple[str, bool, bool]] = []
        #: Whether this is the body of a `$( )`, `<( )` or `>( )`, where bash
        #: ends a body at a line that opens with its delimiter and holds a `)`.
        self.compat = compat
        #: Whether this is the reading `_Lexer.expanded` gives an unquoted
        #: here-document's body (`PL-GJKN`).
        self.expansion = expansion
        #: Whether this is the body of a `$( )` read directly in such a
        #: reading, whose end bash finds by a parse of its own, as
        #: `_Lexer.slipped` reads it (`PL-54MD`).
        self.extracted = False
        #: What bash reads again after the last line inside it that ended a
        #: body early: from the rest of that line to the start of the next,
        #: as `_Lexer.push_back` records it (`PL-54MD`).
        self.pushed: tuple[int, int] | None = None


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
        #: The span of each substitution a here-document's body runs, where the
        #: body is read outside every substitution: each is a piece of
        #: `script_lines` (`PL-55R2`).
        self.expansions: list[tuple[int, int]] = []

    def refuse(self, reason: str) -> None:
        if self.refusal is None:
            self.refusal = reason

    def read(
        self, index: int, stop: int, closes: bool, flat: list[str], backquote: bool = False
    ) -> tuple[tuple[Clause, ...], int]:
        """The clauses from `index`, and the offset just past where they end.

        They end at `stop`, or, where `closes` - the body of a `$(`, `<(` or
        `>(` - at the `)` that closes it, which must come first. `backquote`
        reads a backquote's body, whose unended here-documents bash reads as
        empty rather than carrying them out. The hooks' tokens go to `flat` as
        they are read.
        """
        command = self.command
        frame = _Frame(compat=closes)
        frame.extracted = closes and bool(self.frames) and self.frames[-1].expansion
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
        grammar = _Grammar()

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
                self.refuse("carries a newline, which no admitted shape uses")
                if grammar.conditional:  # inside `[[ ]]`: the bodies start, and the line goes on
                    grammar.condition(char, operator=True)
                    index = self.here_documents(index, stop)
                    continue
                tokens.append(char)
                spans.append((index, index + 1))
                if flat and not (isinstance(flat[-1], Operator) and flat[-1] in HEADS):
                    flat.append(Operator(";"))
                resume = self.here_documents(index, stop)
                if not self.nested:
                    self.breaks.append((index, resume))
                grammar.head, grammar.leading = True, ""
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
            elif char in "<>" and self.process(index, stop):
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
            elif char in "(|" and grammar.conditional == "regex":
                # A regular expression's `(` opens a pair, and its `|` is part
                # of it, as bash reads the word after `=~` (`PL-X1VN`).
                self.refuse(f"carries `{char}`, which no admitted shape uses")
                start()
                end = self.matched(index, stop) if char == "(" else index + 1
                text.append(command[index:end])
                spelled.append(self.kept(index, end))
                index = end
            elif char in SHELL_OPERATORS:
                operator, end = _operator_at(command, index, stop)
                if (
                    operator == "("
                    and begin >= 0
                    and not quoted
                    and not grammar.conditional
                    and _assigns_a_list("".join(text))
                ):
                    self.refuse("carries `(`, which no admitted shape uses")
                    end = self.array(index, stop)
                    text.append(command[index:end])
                    spelled.append(self.kept(index, end))
                    index = end
                    continue
                if (
                    operator == "("
                    and begin < 0
                    and (grammar.head or grammar.counting)
                    and _arithmetic(command, index, stop)
                ):
                    # An arithmetic command, or an arithmetic `for`'s
                    # expressions: one word that runs no command (`PL-3Z8B`).
                    self.refuse("carries `(`, which no admitted shape uses")
                    start()
                    end = self.arithmetic(index, stop)
                    text.append(command[index:end])
                    spelled.append(self.kept(index, end))
                    index = end
                    finish()  # bash reads what follows the `))` as a token of its own
                    continue
                against = begin >= 0 and not quoted and _names_a_descriptor("".join(text))
                finish(redirected=operator[0] in "<>" and not grammar.conditional)
                if grammar.conditional:
                    # Inside `[[ ]]` its own operators are words of it, which no
                    # command runs and none redirects (`PL-X1VN`).
                    if against and operator in ("<", ">"):  # bash reads a NUMBER there, no word
                        raise _Unreadable(f"has a descriptor against `{operator}` in `[[ ]]`")
                    grammar.condition(operator, operator=True)
                    if operator != "&&":
                        self.refuse(f"carries `{operator}`, which no admitted shape uses")
                    self.joins.extend(
                        at for at in range(index + 1, end) if command.startswith("\\\n", at)
                    )
                    tokens.append(Word(operator))
                    spans.append((index, end))
                    flat.append(operator)
                    index = end
                    continue
                if self.introducer is not None:
                    raise _Unreadable("has a `<<` with no word after it")
                self.joins.extend(
                    at for at in range(index + 1, end) if command.startswith("\\\n", at)
                )
                if not grammar.pattern(operator):  # a pattern's `)` neither nests nor closes
                    if closes and operator == ")" and not depth:
                        if frame.extracted:
                            self.slipped(frame, index, end, tokens)
                        flat.append(Operator(operator))
                        self.frames.pop()
                        # Bash reads the bodies still waiting after the line this closes on.
                        self.frames[-1].carried += frame.carried + frame.pending
                        self.introducer = outside
                        return self.cut(tokens, spans), end
                    depth += {"(": 1, ")": -1}.get(operator, 0)
                    grammar.operator(operator)
                if operator != "&&":
                    self.refuse(f"carries `{operator}`, which no admitted shape uses")
                if operator in ("<<", "<<-"):
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
                extglob = char in "@*+?!" and grammar.conditional == "pattern"
                after = (
                    _past_continuations(command, index + 1, stop)
                    if char == "$" or extglob
                    else index
                )
                follows = command[after : after + 1] if after < stop else ""
                if extglob and follows == "(":
                    # An extglob group, a pair as bash reads one in the word
                    # after `==`, `=` or `!=` (`PL-X1VN`).
                    self.joins.extend(range(index + 1, after, 2))
                    end = self.matched(after, stop)
                    spelled.append(self.kept(index, end))
                elif char == "$" and follows == "(" and not _arithmetic(command, after, stop):
                    # Read inline for the hooks, as `$`, `(`, the body and `)`.
                    self.joins.extend(range(index + 1, after, 2))
                    spelled.append(char)
                    end_spelling()
                    flat.append(Operator("("))
                    end = self.substitution_body(index, after + 1, stop, flat)
                elif char == "$" and follows == '"':
                    # A locale string: the double-quoted string, its `$` dropped,
                    # as bash reads one in the C locale (`PL-V690`).
                    self.joins.extend(range(index + 1, after, 2))
                    index = self.double_quoted(after + 1, stop, text, spelled)
                    quoted = True
                    continue
                elif char == "$" and follows == "'":
                    # ANSI-C quoting: its escapes replaced as bash replaces them
                    # in the C locale (`PL-48ZJ`).
                    self.joins.extend(range(index + 1, after, 2))
                    close = self.ansi_c_end(after, stop)
                    decoded = _ansi_c(command[after + 1 : close])
                    text.append(decoded)
                    spelled.append(decoded)
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
        if grammar.conditional:
            # Read on, it would take every line left for the words of its test.
            raise _Unreadable("has an unclosed `[[`")
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
                end = self.substitution(index, stop, quoted=True)
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

    def substitution(self, index: int, stop: int, quoted: bool = False) -> int:
        """The offset past a command substitution opening at `index`, having read its body.

        `index + 1` where none opens there. A `$(` ends at the `)` that closes
        it, read by the same rules as the command, so a `)` inside quotes, a
        subshell or a `case` pattern does not; a backquote ends at the first
        backquote no backslash escapes, as `backquote` reads one, `quoted`
        where double quotes hold it (Bash Reference Manual §3.5.4 "Command
        Substitution"). A `${` is read to the `}` that closes it, as
        `parameter` reads one, and a `$((` bash reads as arithmetic to its
        `))`, as `arithmetic` reads one, a word with no body of its own
        (§3.5.5 "Arithmetic Expansion", `PL-3Z8B`). A backslash-newline after
        the `$` is removed first, as bash removes it before it reads what the
        `$` opens. The hooks' tokens of a body read here go to a list of their
        own in `substituted`, the text staying in the word around it.
        """
        command = self.command
        if command[index] == "`":
            return self.backquote(index, stop, quoted)
        if command[index] != "$":
            return index + 1
        after = _past_continuations(command, index + 1, stop)
        if not command.startswith(("(", "{"), after, stop):
            return index + 1
        self.joins.extend(range(index + 1, after, 2))
        if command[after] == "{":
            return self.parameter(after + 1, stop)
        if _arithmetic(command, after, stop):
            return self.arithmetic(after, stop)
        sink: list[str] = []
        self.substituted.append(sink)
        return self.substitution_body(index, after + 1, stop, sink)

    def substitution_body(self, opening: int, index: int, stop: int, flat: list[str]) -> int:
        """Read the body of the substitution opening at `opening`, from `index`, to its `)`.

        The offset past that `)` is returned.
        """
        self.nested += 1
        clauses, end = self.read(index, stop, closes=True, flat=flat)
        self.nested -= 1
        self.bodies.append((opening, clauses))
        return end

    def backquote(self, index: int, stop: int, quoted: bool = False) -> int:
        """The offset past the backquote closing the one at `index`, having read the command inside.

        Bash ends one at the first backquote no backslash escapes, and reads
        the command inside once each backslash before a backquote, a `$` or
        another backslash is removed - and before a `"`, where double quotes
        hold it - which is how backquotes nest: in ``x=`p \\`p bq\\``` the
        inner `p bq` is a command of its own (POSIX.1-2017 XCU §2.6.3,
        §2.2.3). Read from the raw text, its backquotes were escaped
        characters in two of `p`'s words (`PL-BHS7`). Bash 5.2.21 keeps that
        `\\"` in a double-quoted string inside a `${...}` double quotes hold,
        which is read here as any double-quoted string is.

        A body with no such backslash is read where it stands. One with any is
        read as a command of its own, by a reading of the text bash reads,
        and what that reading found is put back where it stands in the
        command: each of its characters covers the backslash removed before
        it, so a span runs from a word's first written character to its last.
        """
        command = self.command
        close = index + 1
        while close < stop and command[close] != "`":
            close += 2 if command[close] == "\\" else 1
        if close >= stop:
            raise _Unreadable("has an unclosed command substitution")
        sink: list[str] = []
        self.substituted.append(sink)
        escapes = '$`\\"' if quoted else "$`\\"
        body: list[str] = []
        #: Where each character of the body starts in the command, and where it ends.
        starts: list[int] = []
        at = index + 1
        while at < close:
            if command[at] == "\\" and command[at + 1] in escapes:
                body.append(command[at + 1])
                starts.append(at)
                at += 2
                continue
            body.append(command[at])
            starts.append(at)
            at += 1
        starts.append(close)
        self.nested += 1
        if len(body) == close - index - 1:
            clauses, _ = self.read(index + 1, close, closes=False, flat=sink, backquote=True)
            self.nested -= 1
            self.bodies.append((index, clauses))
            return close + 1
        inner = _Lexer("".join(body), bash_c=self.bash_c)
        inner.nested = self.nested
        try:
            clauses, _ = inner.read(0, len(body), closes=False, flat=sink, backquote=True)
        finally:
            self.nested -= 1
            # What its reading found, put where it stands: a continuation by
            # the backslash just before its newline, which is never escaped.
            self.substituted += inner.substituted
            self.joins += [starts[join + 1] - 1 for join in inner.joins]
            self.removed += [(starts[first], starts[last]) for first, last in inner.removed]
            self.bodies += [(starts[at], self.placed(found, starts)) for at, found in inner.bodies]
            if inner.refusal is not None:
                self.refuse(inner.refusal)
        self.bodies.append((index, self.placed(clauses, starts)))
        return close + 1

    def placed(self, clauses: tuple[Clause, ...], starts: list[int]) -> tuple[Clause, ...]:
        """Clauses read from a backquote's body, their spans put where they stand in the command.

        `starts` gives where each character of the body starts, and where the
        last ends; each clause is spelled as the command spells it.
        """
        placed: list[Clause] = []
        for clause in clauses:
            spans = tuple((starts[first], starts[last]) for first, last in clause.spans)
            spelled = self.command[spans[0][0] : spans[-1][1]] if spans else ""
            placed.append(Clause(spelled, clause.tokens, spans))
        return tuple(placed)

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

    def arithmetic(self, index: int, stop: int) -> int:
        """The offset past the `))` closing the arithmetic whose first `(` stands at `index`.

        `_arithmetic` has found it one: an arithmetic command, an arithmetic
        `for`'s expressions or a `$(( ))`. Bash reads what stands between as
        one pair, as `matched` reads one, the `)` closing its second `(`
        followed at once by another (Bash Reference Manual §3.2.5.2
        "Conditional Constructs", §3.5.5 "Arithmetic Expansion"). It runs no
        command of its own, so it holds no body (`PL-3Z8B`).
        """
        command = self.command
        second = _past_continuations(command, index + 1, stop)
        self.joins.extend(range(index + 1, second, 2))
        return self.matched(second, stop) + 1  # past the `)` `_arithmetic` found after it

    def matched(self, index: int, stop: int) -> int:
        """The offset past the `)` closing the `(` at `index`, read as bash reads a matched pair.

        As bash 5.2.21's `parse_matched_pair` reads one: it counts
        parentheses, steps over quotes, backslash escapes and a `$'...'`, and
        reads each `$` expansion and backquote it meets as `substitution` does,
        so a command substitution inside still runs a command, while a `#`, a
        newline and a `<<` are characters of the pair. Unreadable where
        nothing closes it.
        """
        command = self.command
        depth = 0
        at = index
        while at < stop:
            char = command[at]
            if char in "()":
                depth += 1 if char == "(" else -1
                at += 1
                if not depth:
                    return at
            elif char == "\\":
                if command.startswith("\n", at + 1, stop):
                    self.joins.append(at)
                at += 2
            elif char == "'":
                end = command.find("'", at + 1, stop)
                if end < 0:
                    raise _Unreadable("has an unbalanced quote")
                at = end + 1
            elif char == '"':
                at = self.double_quoted(at + 1, stop, [], [])
            elif char == "$" and command.startswith(
                "'", after := _past_continuations(command, at + 1, stop), stop
            ):
                self.joins.extend(range(at + 1, after, 2))
                at = self.ansi_c_end(after, stop) + 1
            else:
                at = self.substitution(at, stop)
        raise _Unreadable("has an unclosed `(`")

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
        self.push_back(resume, after_compat)
        if index != after_compat:
            # The bodies after the one ended early took the lines after its
            # own, so reading jumps past them once the rest of it is read.
            self.jumps[after_compat] = index
        return resume

    def push_back(self, rest: int, after: int) -> None:
        """Record that bash reads from `rest` to `after` again, for `slipped`.

        That is the rest of a line that ended a body early, which bash pushes
        back into its input, newline and all (`shell_ungets` in bash 5.2.21's
        parse.y, called from `make_here_document` in make_cmd.c). It counts on
        the `$( )` an expanded body runs where the line ended a body of that
        one or of a `$( )` inside it, since bash's parse for its end reads
        those as it goes, and not inside a backquote or a nested body's
        expansion, which that parse reads past as text (`PL-54MD`).
        """
        for frame in reversed(self.frames):
            if frame.extracted:
                frame.pushed = (rest, after)
                return
            if not frame.compat:
                return

    def slipped(self, frame: _Frame, index: int, end: int, tokens: list[Word | str]) -> None:
        """Read the end bash finds for the `$( )` an expanded body runs, its `)` at `index`.

        Bash 5.2.21 finds it with a parse of its own (`xparse_dolparen` in
        parse.y), whose `rewind_input_string` takes the offset reading reached,
        less what is unread of the current line and one more for the newline
        that line's length leaves out. A line `push_back` recorded has its
        newline counted in, so where this `)` is read from one, the offset
        comes out a character early, on whatever bash read before the `)`.
        Where that is not a `)`, bash finds none closing the substitution, and
        the expansion fails: unreadable here. Where it is one, bash takes that
        one for the end, runs the text up to it, and expands what follows as
        text, which the `_Cut` it raises goes on past. The text leaves open
        what that `)` closed, so where the substitution holds no newline of
        its own, bash's run is one syntax error and runs nothing; with one, the
        lines before it run, and an escaped `)` closes nothing, so both are
        read as the parse found them, every command bash runs among what it
        reads (`PL-54MD`, `PL-H710`).
        """
        if frame.pushed is None or not frame.pushed[0] <= index < frame.pushed[1]:
            return
        command = self.command
        before = index - 1
        while command[before] == "\n" and before - 1 in self.joins:  # bash removed the pair
            before -= 2
        if command[before] != ")":
            raise _Unreadable("has a substitution bash finds no `)` to close")
        escapes = 0
        while before - escapes > 0 and command[before - escapes - 1] == "\\":
            escapes += 1
        if not escapes % 2 and "\n" not in tokens:
            raise _Cut(end)

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
        carried out of its substitution. Bash reads the rest of that line again
        from the input, and inside a `$( )` an unquoted here-document's body
        runs, where that can move the end bash finds for it, `push_back`
        records where (`PL-54MD`). Bash reads a body its delimiter never ends
        to the end of the input, with a warning; here that is unreadable unless
        the input is read
        as `bash -c` reads it, so that a `<<` docket took for one leaves what
        follows it declined rather than read as a body unannounced. Where no
        part of the delimiter was quoted, `joined`, bash expands the body once
        it has found where the body ends, and `expanded` reads the commands
        that expansion runs.
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
        `Reading.substitutions` and `FlatReading.substituted`. Where the
        here-document's body is read outside every substitution, each
        substitution's span goes into `expansions` too, which `script_lines`
        hands on as a piece of its own (`PL-55R2`). Bash 5.2.21 expands the
        body only once its delimiter has ended it, so one the delimiter line
        cuts, or one never closed, fails that expansion with an error and the
        script runs on: it is read as the text it is, and nothing reading it
        began is kept. Bash expands nothing in the body past it either, so a
        substitution after one that failed runs nothing and is not read. One
        fails too, or is cut short and runs nothing while the expansion goes
        on, where bash finds its end a character early, as `slipped` reads it:
        `$(echo inner <<F` over `F)` closes at the top level and fails here
        (`PL-GJKN`, `PL-54MD`).
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
            introducer, jumps, expansions = self.introducer, dict(self.jumps), len(self.expansions)
            # Its own reading: a here-document it leaves unended is not carried out.
            self.frames.append(_Frame(compat=False, expansion=True))
            try:
                after = self.substitution(at, end)
            except (_Unreadable, _Cut) as stopped:
                del self.bodies[bodies:], self.substituted[substituted:], self.joins[joins:]
                del self.removed[removed:], self.frames[frames:], self.expansions[expansions:]
                self.nested, self.introducer, self.jumps = nested, introducer, jumps
                if isinstance(stopped, _Unreadable):
                    return
                at = stopped.after  # it runs nothing, and the expansion goes on past it
                continue
            self.frames.pop()
            if not nested and len(self.bodies) > bodies:  # a `${x}` or `$((1))` runs nothing
                self.expansions.append((at, after))
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
    `$` and a backtick; `$"..."` is the `"..."` it holds, as bash reads it in
    the C locale, translating nothing (§3.1.2.5 "Locale-Specific Translation",
    `PL-V690`); in `$'...'` it escapes the next character, an
    apostrophe included, and each escape is replaced as bash replaces it in
    the C locale (`PL-48ZJ`); outside quotes it escapes the next character; an
    operator is the longest match in `OPERATORS`, read across any
    backslash-newline inside it; `#` opens a comment only where no word is in
    progress, and it runs to the end of its line; a `${...}` is part of its
    word, to the `}` that closes it; a `$( )`, a `<( )`, a `>( )` or a
    backquote, quoted or not, or inside a `${...}`, runs a command, so its body
    is read by these same rules into `Reading.substitutions`, a backquote's
    once the backslashes bash removes from it are gone (`PL-BHS7`); and
    `name=(` opens an array assignment, one word to its `)`. A newline is
    read as bash reads one, though no field holds one, because `script_lines`
    hands this a script's lines: a backslash before it removes both, quoted or
    not, as long as it is not in single quotes; unquoted, it ends a command as
    `;` does, and the bodies of the here-documents a `<<` or `<<-` opened
    before it are skipped to their delimiters, in logical lines where no part
    of the delimiter is quoted (§3.1.2.1 "Escape Character", §3.6.6 "Here
    Documents"). Bash's compound commands bend that, and `_Grammar` follows
    them: a `case` pattern's `)` closes no `$(`, and inside `[[ ]]` or an
    array assignment a newline ends no command, though the bodies waiting on
    it start after it. Inside `[[ ]]` an `&&`, `||`, `(`, `)`, `<` and `>`
    are words of the conditional, the word after `=~` holds a regular
    expression's groups and bars, and the word after `==`, `=` or `!=` a
    pattern's extglob groups (§3.2.5.2 "Conditional Constructs",
    `PL-X1VN`). An arithmetic `(( ))` or `$(( ))` is one word, read as bash
    5.2.21's `parse_matched_pair` reads one, so a newline there is a space
    and a `<<` a shift, and only a substitution inside runs a command (§3.5.5
    "Arithmetic Expansion", `PL-3Z8B`). Not read, as bash would read them: a
    command run through `sh -c` or `eval`. The admitted shapes refuse a
    `$'...'` at its `$`, though it is read to its end (`PL-C45K`).

    Every operator is read rather than stopped at, because a pipe answering
    with another command's status is what the `-k` rule looks for. Every one
    but `&&` is also a refusal where it comes first: a pipe answers with
    another command's status, `||` and `;` replace or discard a failure, a
    redirection or a subshell is a shape nobody has argued for. So are an
    unquoted character outside `PLAIN` and a `$` or backtick inside double
    quotes, where the shell expands it. A command the shell cannot read - an
    unbalanced quote, a trailing backslash, an unclosed substitution or `[[`,
    a `[[ ]]` whose grammar bash refuses, a `<<` with no word after it, a
    here-document its delimiter never ends -
    has no clauses, and its refusal says why unless something earlier already
    had.
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
    quote, an unclosed substitution or `[[`, a `<<` with no word after it -
    leaves it incomplete.
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
    "Arrays"). All but a substitution in the body of a delimiter with no
    quoted part, which bash expands and so runs (`PL-P95F`): each is a piece
    of its own after its line's, spelled from its `$` or backquote, so
    `shell_words` reads it as one word whose substitution is the command bash
    runs (`PL-55R2`). A body a `<<` ahead of a substitution opened starts
    after the line the substitution closes on, as bash reads it (`PL-QSN5`).
    A newline after `&&` or `|` ends a piece too: the command goes on, and
    each piece still reads whole.

    Each piece is spelled as the script spells it, from where its line starts
    to the newline ending it, or from where its substitution opens to where it
    closes, so `shell_words` reads it as it stands in the script. Its
    continuations, and the body of any here-document opened inside a
    substitution, are left for that reading to remove: cut out here, a body
    would leave its `<<` to take whatever line came next. Where the script
    stops being readable, everything from the start of that line is one
    piece, which `shell_words` declines in turn.
    """
    lexer = _Lexer(script, bash_c=False)
    try:
        lexer.read(0, len(script), closes=False, flat=[])
    except _Unreadable:
        pass  # the lines before it stand; the rest is the last piece, read as unreadable
    pieces: list[tuple[str, int]] = []
    start = 0
    expansions = iter(lexer.expansions)
    expansion = next(expansions, None)
    for end, resume in lexer.breaks:
        pieces.append((script[start:end], start))
        while expansion is not None and expansion[0] < resume:
            if expansion[0] > end:  # after the line, not in a body a `[[ ]]` or array read
                pieces.append((script[expansion[0] : expansion[1]], expansion[0]))
            expansion = next(expansions, None)
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
