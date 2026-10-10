"""How bash splits a command line, for the four Bash guard hooks to share.

`gate-status-guard.sh`, `floor-interpreter-guard.sh`, `no-prune-guard.sh` and
`push-check-guard.sh` each decide on a command string before it runs, so each
has to know where one
command ends and the next begins. Each used to spell that itself - two
`shlex.shlex(punctuation_chars=True)` lexers behind a newline substitution, and
a regex - and each copy read some shape differently from bash. A `)` glued to
the `;` after it hid the separator (`PL-63TT`), a backslash-newline read as one
(`PL-R5RF`), and everything after the first `<<` was dropped rather than only
the heredoc's body (`PL-39LD`). Those are one question answered three times,
which is `PL-PVW2`'s fact, and this module is the one answer the hooks import.

**The reading itself is docket's** (`PL-JNYL`). This module held a lexer of
its own beside `subprojects/docket/src/docket/shell.py`, and `#1377` found and
fixed the same three bash facts in each. So it reads a command through that
module's `flat_reading`, having put docket's `src` on `sys.path`, found from
this file's own place: one pass decides where a word, a quote, an operator, a
line, a here-document's body and a substitution end, for docket and the hooks
alike, and that module names the bash rules it follows. What this module is
handed is the hooks' view of that reading. Each word comes with its quotes
removed, an operator as `Operator` and a redirection's descriptor as
`Descriptor`; a newline that ends a command is `;`, except after a separator
or `(`, where bash reads a linebreak; every comment, continuation and
here-document body is gone; and an unquoted `$( )`, `<( )` or `>( )` is read
inline, its parentheses as operators, so a substitution's parentheses reach a
walker counting subshells as they always have. It is read as `bash -c` reads
the string the harness hands it, so a here-document its delimiter never ends
runs to the end of the input and a trailing backslash is a backslash, as bash
5.2.21 runs them.

**Where a command's words start is answered here too**, by `command_words`,
so no guard can disagree with another about which word is the command. It
drops everything bash reads ahead of a command's name, the reserved words that
open a command included: `do make check` runs `make`, where it once read as a
command named `do` and passed all three guards (`PL-0X0G`). A redirection is
among them, and is no word of the command wherever it stands: bash lifts it out
before it runs anything, so `2>/dev/null make check` runs `make` and `echo a
2>&1 b` prints `a b` (`PL-K9QL`). It takes its operator, the word after it, and
the descriptor written against it - a number or a `{name}` with no space before
a `<` or `>` operator, unquoted - so `timeout 5>x make check` hands `timeout` no
duration, where `timeout 5 >x` and `timeout '5'>x` do. And `commands`
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

**And which builtin a command runs in this shell**, by `builtin_words`, which
reads past `command` and `builtin` only: they run a builtin in the shell itself,
so `command set -o pipefail` holds for the pipe after it, where `timeout 5 set`
looks for a program named `set` and finds none (`PL-9RSP`). Each is read bare,
because a `command` named by path is a program, and `command` by the grammar
`WRAPPERS` holds for it, so the two readers cannot disagree about its options.

**Last, how to spell a command back so that bash runs it again**, by
`command_line`, for a guard that prints one to be run: spelled from the
program's name alone, the gate guard's remedy for `python3 tools/doc_check.py
check` was `tools/doc_check.py`, and no `tools/` script is executable
(`PL-ZS13`). It says what of the quoting `words` removed it cannot restore.

**What it does not read**, none of which a guard here has needed: the `&&`,
`||`, `<` and `>` inside `[[ ]]`, which read as a separator or a redirection,
the command a `coproc` runs, a wrapper `WRAPPERS` does not name (`sudo`,
`stdbuf`, a `time` run by path), and the string `env -S` splits, for which
`program_words` reads no program at all. A reserved word opens a command here
only at the head of its segment, so `command_words` does not reach the `make
check` in `if (true) then make check; fi` or in `for f do make check; done`;
`commands` reads the first, splitting at its `)`. And a quoted `if` or `{`, or
a `time` after a `|`, reads as the reserved word, where bash reads a command's
name. This list is the construct side of the three guards' known gaps
(`PL-61FT`): bash's grammar is read as far as sessions write it around a
guarded command, so a construct found missing only by probing is added here
rather than filed. Arithmetic, a `case` pattern's `)`, a newline inside `[[ ]]`
and a backquote's body left it with the merge, since docket's reading reads
all four (`PL-JNYL`): a `<<` inside `(( ))` is a shift rather than a
here-document swallowing the lines after it, a backquote's command is read as
a command it runs, and a pattern's `)` closes no `$( )` around it, though
`words` still hands it over as the operator `)` a subshell closes with.

A redirection with no word after it, which bash refuses, is read as taking only
its operator, and a `<(` or `>(` as the process substitution it is rather than
a redirection. A command bash would refuse - an unclosed quote or
substitution, a `<<` with no word after it - is unreadable. `words` and
`segments` answer None for it, and the gate and floor guards fail open on that,
as they always have. `commands` still reads it as far as it can, because bash
runs every line before the one it cannot finish. Standard library only, and it
parses at the floor `tests/unit/test_tools_portability.py` holds
`.claude/hooks/` to. Every guard pays its import on every Bash call, so it
loads nothing the guard has not already loaded but itself and docket's
`shell.py`, and `tests/unit/test_shell_reader.py` holds it to that.
"""

import os
import re
import sys

# docket's `src`, from this file's own place, since a guard puts only
# `.claude/hooks/` on the path and `bin/docket` only docket's own (`PL-JNYL`).
_HERE = os.path.dirname(os.path.abspath(__file__))
_DOCKET = os.path.normpath(
    os.path.join(_HERE, os.pardir, os.pardir, "subprojects", "docket", "src")
)
if _DOCKET not in sys.path:
    sys.path.insert(0, _DOCKET)

from docket.shell import Descriptor, Operator, flat_reading  # noqa: E402


class Command(list[str]):
    """A command's words from the program it runs, and the wrappers read past to reach it.

    `xargs -I % git branch -dr origin/%` runs `git` with names `xargs` reads
    from its input, so its words alone read as one ref spelled out, and only the
    wrapper says otherwise (`PL-G8TR`).
    """

    def __init__(self, words: list[str], wrappers: tuple[str, ...] = ()) -> None:
        super().__init__(words)
        # Each wrapper's name, bare, outermost first: `timeout 5 xargs git` gives both.
        self.wrappers = wrappers


# The operators that redirect, each taking the word after it. Only those opening
# with `<` or `>` take a descriptor: in `echo hi 2&>x` the `2` is a word.
REDIRECTIONS = frozenset("< << <<- <<< <& <> > >> >& >| &> &>>".split())

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

# What makes bash read a word written bare as something else: a blank splits
# it, a quote or a backslash is read as quoting, an operator character ends it,
# and a `#` can open a comment. A `$`, a backtick and the glob characters are
# not here, so a word bash expanded is expanded again (`PL-ZS13`).
NEEDS_QUOTES = re.compile(r"[\s'\"\\&|;()<>#]")


class Grammar:
    """How one wrapper reads the words ahead of the command it runs, as GNU getopt reads them.

    A plain class rather than a `NamedTuple`, whose `typing` would cost every
    guard's import on every Bash call (`PL-JNYL`).
    """

    def __init__(
        self,
        valued: str = "",
        optional: str = "",
        flags: str = "",
        long_valued: tuple[str, ...] = (),
        long_other: tuple[str, ...] = (),
        stops: frozenset[str] = frozenset(("help", "version")),
        operands: int = 0,
    ) -> None:
        # Short options whose value is the rest of the word, or else the next word.
        self.valued = valued
        # Short options whose value is only ever the rest of the word.
        self.optional = optional
        # Short options taking no value, which a bundle may run on after.
        self.flags = flags
        # Long options whose value follows an `=`, or else is the next word; each
        # may be abbreviated to any prefix no other long option shares.
        self.long_valued = long_valued
        # Long options taking a value only after an `=`, and those taking none.
        self.long_other = long_other
        # Options after which no program is read: one that describes a command
        # rather than running it, or one that runs a string this does not split.
        self.stops = stops
        # The words read between the options and the command: a duration.
        self.operands = operands


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

# The builtins that run another builtin in this shell (`help command` and `help
# builtin` in bash 5.2.21): `command` by its grammar as a wrapper, and `builtin`,
# which refuses any option but `--`. Named bare, since a path names a program.
RUN_A_BUILTIN = {"command": WRAPPERS["command"], "builtin": Grammar()}

# `nice`'s older spelling of an adjustment: `nice -5` and `nice --5`.
NICE_ADJUSTMENT = re.compile(r"^-[-+]?\d")


def words(command: str) -> list[str] | None:
    """The tokens bash reads in `command`, or None where bash would refuse it.

    Words come with their quotes removed, operators as `Operator` and a
    redirection's descriptor as `Descriptor`, with each newline that ends a
    command read as `;` and every comment, continuation and heredoc body gone,
    as `docket.shell.flat_reading` reads them.
    """
    reading = flat_reading(command)
    return list(reading.tokens) if reading.complete else None


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
    then any assignments and redirections, in any order (POSIX.1-2017 XCU
    §2.9.1). Those come last because bash reads a reserved word only as a
    command's first word: after `FOO=1` or `2>/dev/null`, `if` and `time` are
    the names of programs, which bash 5.2.21 reports it cannot find (`PL-0X0G`,
    `PL-K9QL`). A redirection after the command word is left where it stands,
    so the words dropped are always the ones ahead of what is returned.

    Every guard reads the head of a command through this, so none can disagree
    with another about which word is the command - as two readers inside one
    hook once did, and a `set` opening a group went unseen (`PL-1SFZ`).
    """
    rest = _past_openers(segment)
    while rest:
        taken = 1 if ASSIGNMENT.match(rest[0]) else _redirection(rest, 0)
        if not taken:
            break
        del rest[:taken]
    return rest


def _past_openers(segment: list[str]) -> list[str]:
    """`segment` past the grouping and reserved words opening its command, and `time`'s options."""
    rest = list(segment)
    while rest and (rest[0] in GROUPING or rest[0] in OPENS_A_COMMAND):
        if rest.pop(0) == "time":
            for option in TIME_OPTIONS:
                if rest and rest[0] == option:
                    rest.pop(0)
    return rest


def command_line(segment: list[str]) -> str | None:
    """The command `segment` runs, spelled so that bash runs it again, or None where it cannot be.

    Its assignments, its command word and its arguments, in order and through
    any wrapper, less what bash reads around them: the grouping and reserved
    words `command_words` drops, every redirection, which bash lifts out
    wherever it stands, and a `)` closing a subshell opened before the
    segment. For a guard printing a command back to be run, which has to run
    what the segment ran (`PL-ZS13`).

    A word is quoted only where bash would read it bare as something else, and
    in double quotes where it holds a `$` or a backtick, so what bash expanded
    is expanded again - and a `$` that single quotes hid comes back live, since
    `words` keeps no record of which quote it was. An unquoted substitution
    reaches here as operators with the quoting inside it gone, so a segment
    holding one answers None rather than a spelling that runs something else.
    """
    spelled: list[str] = []
    for word in _lift(_past_openers(segment))[0]:
        if isinstance(word, Operator) and word == ")":
            continue
        if isinstance(word, Operator):
            return None
        spelled.append(_quoted(word))
    return " ".join(spelled) or None


def _quoted(word: str) -> str:
    """`word` written so that bash reads it back as this word: bare where it can be.

    An assignment keeps its `NAME=` bare and has its value quoted, since
    quoted whole it would be a command's name rather than an assignment.
    """
    name = ASSIGNMENT.match(word)
    head = name.group() if name else ""
    value = word[len(head) :]
    if (value or head) and not NEEDS_QUOTES.search(value):
        return word
    if "$" in value or "`" in value:
        return head + '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'
    import shlex  # only a guard printing a command back pays for it

    return head + shlex.quote(value)


def program_words(segment: list[str]) -> Command:
    """`segment` from the program it runs: its command word, or past each wrapper ahead of it.

    `timeout 60 nice -n 5 git fetch --prune` runs `git`, so that is where the
    words start (`PL-TRMN`), and the wrappers read past are kept beside them.
    Every redirection is gone from what is returned, since bash passes none of
    them to the program: `env 2>/dev/null git fetch --prune` runs `git`, and
    `bin/docket 2>/dev/null check` hands `bin/docket` the word `check` first
    (`PL-K9QL`). Empty where the wrapper runs nothing -
    `command -v git` describes it, a wrapper given no command runs none, and
    one refusing an option it does not know stops there - or runs a string this
    does not read, as `env -S` does.
    """
    rest, _ = _lift(command_words(segment))
    wrappers: list[str] = []
    while rest and _basename(rest[0]) in WRAPPERS:
        wrappers.append(_basename(rest[0]))
        rest = _run_by(rest, WRAPPERS)
    return Command(rest, tuple(wrappers))


def builtin_words(segment: list[str]) -> list[str]:
    """`segment` from the builtin it runs in this shell, past each `command` and `builtin`.

    Those two run a builtin in the shell itself, so `command set -o pipefail`
    holds for the pipe after it, where a wrapper in `WRAPPERS` runs a program
    and `timeout 5 set` finds none named `set` (`PL-9RSP`). Redirections are
    gone, as from `program_words`. Empty where `command -v` describes the
    builtin rather than running it, or `builtin` is given an option it refuses.
    """
    rest, _ = _lift(command_words(segment))
    while rest and rest[0] in RUN_A_BUILTIN:
        rest = _run_by(rest, RUN_A_BUILTIN)
    return rest


def redirections(segment: list[str]) -> list[tuple[str, str, str]]:
    """Each redirection in `segment`, wherever it stands: its descriptor, its operator and its word.

    A descriptor not written is "", and so is the word of an operator bash
    would refuse for having none. For a guard reading what a command is handed
    apart from its words, as the floor guard reads a file redirected onto an
    interpreter's standard input (`PL-K9QL`).
    """
    _, lifted = _lift(segment)
    return lifted


def _redirection(words: list[str], at: int) -> int:
    """How many of `words` the redirection starting at `at` takes, or 0 where none starts there.

    Its descriptor where one is written against it, its operator, and the word
    it names. A `<(` or `>(` starts a process substitution, not a redirection,
    and an operator with no word after it takes only itself.
    """
    end = at + 1 if isinstance(words[at], Descriptor) else at
    if end == len(words) or not (isinstance(words[end], Operator) and words[end] in REDIRECTIONS):
        return 0
    operator, end = words[end], end + 1
    if end < len(words) and not isinstance(words[end], Operator):
        return end + 1 - at
    if end < len(words) and words[end] == "(" and operator in ("<", ">"):
        return 0
    return end - at


def _lift(words: list[str]) -> tuple[list[str], list[tuple[str, str, str]]]:
    """`words` apart from their redirections, and the redirections, as bash lifts them out."""
    kept: list[str] = []
    lifted: list[tuple[str, str, str]] = []
    at = 0
    while at < len(words):
        taken = _redirection(words, at)
        if not taken:
            kept.append(words[at])
            at += 1
            continue
        parts = words[at : at + taken]
        descriptor = parts.pop(0) if isinstance(parts[0], Descriptor) else ""
        operator = parts.pop(0)
        lifted.append((descriptor, operator, parts[0] if parts else ""))
        at += taken
    return kept, lifted


def _basename(word: str) -> str:
    return word.rsplit("/", 1)[-1]


def _long_option(grammar: Grammar, written: str) -> str | None:
    """The long option `written` names, whole or as an abbreviation getopt accepts, or None."""
    names = (*grammar.long_valued, *grammar.long_other, "help", "version")
    if written in names:
        return written
    matching = [name for name in names if name.startswith(written)]
    return matching[0] if len(matching) == 1 else None


def _run_by(words: list[str], grammars: dict[str, Grammar]) -> list[str]:
    """The words of the command the word opening `words` runs, read by its grammar in `grammars`.

    Or [] where it runs none, as `program_words` and `builtin_words` say.
    """
    name = _basename(words[0])
    grammar = grammars[name]
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


def commands(command: str) -> list[Command]:
    """Every command in `command` that bash would run, each read through `program_words`.

    Each carries the wrappers that run it, so a guard can tell `xargs git
    branch -dr` from `git branch -dr` (`PL-G8TR`).

    A segment ends only at a separator; a command also starts after each `(`
    or `)` read as an operator, so a subshell, a `$( )`, a `<( )` and the
    command after a `case` pattern each yield their own. The commands in a
    substitution inside double quotes, a `${...}`, backquotes or an array
    assignment are read too: their text stays in the word, and they run all
    the same.

    Never None, unlike `words` and `segments`. Where bash would refuse the
    command, it has still run every line before the one it could not finish,
    so what could be read before that point is returned rather than nothing.
    """
    reading = flat_reading(command)
    found: list[Command] = []
    for tokens in (reading.tokens, *reading.substituted):
        for segment, _ in _cut(list(tokens)):
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
