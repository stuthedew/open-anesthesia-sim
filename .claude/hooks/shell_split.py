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
not - it looks in the project's environment first - so `program_words` stops
at it, and `uv_run_words` reads past it, and past the options of `uv` and of
`run` on either side of it, for a guard that chooses to: the gate guard alone
(`PL-QMN0`).

**And which builtin a command runs in this shell**, by `builtin_words`, which
reads past `command` and `builtin` only: they run a builtin in the shell itself,
so `command set -o pipefail` holds for the pipe after it, where `timeout 5 set`
looks for a program named `set` and finds none (`PL-9RSP`). Each is read bare,
because a `command` named by path is a program, and `command` by the grammar
`WRAPPERS` holds for it, so the two readers cannot disagree about its options.

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

A redirection with no word after it, which bash refuses, is read as taking only
its operator, and a `<(` or `>(` as the process substitution it is rather than
a redirection. A command bash would refuse - an unclosed quote or
substitution, a `<<` with no word after it - is unreadable. `words` and
`segments` answer None for it, and the gate and floor guards fail open on that,
as they always have. `commands` still reads it as far as it can, because bash
runs every line before the one it cannot finish. Standard library only, and it
parses at the floor `tests/unit/test_tools_portability.py` holds
`.claude/hooks/` to.
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


class Descriptor(str):
    """The descriptor a redirection names ahead of its operator: `2` in `2>&1`, `fd` in `{fd}>x`.

    POSIX calls it IO_NUMBER (XCU §2.10.1), and bash also takes a `{name}` there
    (Bash Reference Manual §3.6 "Redirections"). Spaced from the operator or
    quoted it is an ordinary word, so it cannot be a plain string either.
    """

    __slots__ = ()


# Bash's control and redirection operators, matched longest first.
OPERATORS = frozenset("; ;; ;& ;;& & && &> &>> | || |& ( ) < << <<- <<< <& <> > >> >& >|".split())
OPERATOR_CHARACTERS = frozenset("&|;()<>")

# The operators that redirect, each taking the word after it. Only those opening
# with `<` or `>` take a descriptor: in `echo hi 2&>x` the `2` is a word.
REDIRECTIONS = frozenset("< << <<- <<< <& <> > >> >& >| &> &>>".split())
DESCRIPTOR = re.compile(r"[0-9]+|\{[A-Za-z_][A-Za-z0-9_]*\}")

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

# The builtins that run another builtin in this shell (`help command` and `help
# builtin` in bash 5.2.21): `command` by its grammar as a wrapper, and `builtin`,
# which refuses any option but `--`. Named bare, since a path names a program.
RUN_A_BUILTIN = {"command": WRAPPERS["command"], "builtin": Grammar()}

# The options `uv` reads as its own, which it takes ahead of its subcommand and,
# being global, after `run` too, and then those `run` adds. From `uv --help` and
# `uv run --help` in uv 0.12.19 and the clap definitions behind them, hidden
# ones included (`crates/uv-cli/src/lib.rs` and `crates/uv-cache/src/cli.rs` at
# tag 0.12.19), each run as `uv OPTION --help` and `uv run OPTION --help`: clap
# answers a flag with its help, an option taking a value with "a value is
# required", and one it does not know with "unexpected argument" (`PL-QMN0`).
# `-h`, `-V` and anything not listed run nothing, as in uv.
#
# Clap is not getopt in two ways `_run_by` does not model: it takes no
# abbreviation of a long option, and no value that starts with a dash. Either
# is a command uv refuses to run, so reading it the getopt way can refuse a
# command that fails anyway and passes none that runs a gate. An option a later
# uv adds reads as one it does not know, so a gate after it passes, as one
# behind a wrapper `WRAPPERS` does not name does.
_UV_FLAGS = tuple(
    """
    allow-python-downloads isolated managed-python native-tls no-cache
    no-cache-dir no-color no-config no-installer-metadata no-managed-python
    no-native-tls no-offline no-preview no-progress no-python-downloads
    no-system-certs offline preview quiet show-settings system-certs verbose
    """.split()
)
_UV_VALUED = tuple(
    """
    allow-insecure-host cache-dir color config-file directory preview-feature
    preview-features project python-fetch python-preference trusted-host
    """.split()
)
UV = {
    "uv": Grammar(flags="nqv", long_valued=_UV_VALUED, long_other=_UV_FLAGS),
    "run": Grammar(
        valued="CPfipw",
        flags="Umnqsv",
        long_valued=(
            *_UV_VALUED,
            *"""
            config-setting config-settings config-settings-package default-index
            env-file exclude-newer exclude-newer-package extra extra-index-url
            find-links fork-strategy group index index-strategy index-url
            keyring-provider link-mode max-recursion-depth no-binary-package
            no-build-isolation-package no-build-package no-editable-package no-extra
            no-group no-sources-package only-group package prerelease prerelease-package
            python python-platform refresh-package reinstall-package resolution
            upgrade-group upgrade-package with with-editable with-requirements
            """.split(),
        ),
        long_other=(
            *_UV_FLAGS,
            *"""
            active all-extras all-groups all-packages binary build build-isolation
            compile compile-bytecode dev editable exact force-reinstall frozen
            gui-script inexact locked module no-active no-all-extras no-binary no-build
            no-build-isolation no-compile no-compile-bytecode no-default-groups no-dev
            no-editable no-env-file no-exact no-frozen no-index no-locked no-project
            no-refresh no-reinstall no-sources no-sync no-upgrade no_workspace only-dev
            pre refresh reinstall script show-resolution upgrade
            """.split(),
        ),
    ),
}

# `nice`'s older spelling of an adjustment: `nice -5` and `nice --5`.
NICE_ADJUSTMENT = re.compile(r"^-[-+]?\d")


def words(command: str) -> list[str] | None:
    """The tokens bash reads in `command`, or None where bash would refuse it.

    Words come with their quotes removed, operators as `Operator` and a
    redirection's descriptor as `Descriptor`, with each newline that ends a
    command read as `;` and every comment, continuation and heredoc body gone.
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
    rest = list(segment)
    while rest and (rest[0] in GROUPING or rest[0] in OPENS_A_COMMAND):
        if rest.pop(0) == "time":
            for option in TIME_OPTIONS:
                if rest and rest[0] == option:
                    rest.pop(0)
    while rest:
        taken = 1 if ASSIGNMENT.match(rest[0]) else _redirection(rest, 0)
        if not taken:
            break
        del rest[:taken]
    return rest


def program_words(segment: list[str]) -> list[str]:
    """`segment` from the program it runs: its command word, or past each wrapper ahead of it.

    `timeout 60 nice -n 5 git fetch --prune` runs `git`, so that is where the
    words start (`PL-TRMN`). Every redirection is gone from what is returned,
    since bash passes none of them to the program: `env 2>/dev/null git fetch
    --prune` runs `git`, and `bin/docket 2>/dev/null check` hands `bin/docket`
    the word `check` first (`PL-K9QL`). Empty where the wrapper runs nothing -
    `command -v git` describes it, a wrapper given no command runs none, and
    one refusing an option it does not know stops there - or runs a string this
    does not read, as `env -S` does.
    """
    rest, _ = _lift(command_words(segment))
    while rest and _basename(rest[0]) in WRAPPERS:
        rest = _run_by(rest, WRAPPERS)
    return rest


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


def uv_run_words(words: list[str]) -> list[str] | None:
    """`words` from the command the `uv run` opening them runs, or None where they open none.

    `uv run --with pytest-xdist pytest -n 4` runs `pytest`, and read from the
    word after `run` it was a command named `--with` (`PL-QMN0`). uv takes its
    own options ahead of `run` as well - `uv -q run pytest` - so the options on
    both sides are read, each by its grammar in `UV`. Empty where the `uv run`
    runs nothing: `uv run --help`, an option uv does not know, or no command.

    `words` are a program's, as `program_words` returns them, which does not
    call this: uv looks for the command in the project's environment first, so
    `uv run python3` is the project's interpreter and not the bare one the floor
    guard refuses, and which guard reads past `uv run` is that guard's choice.
    """
    if not words or _basename(words[0]) != "uv":
        return None
    rest = _run_by(words, UV)
    if rest[:1] != ["run"]:
        return None
    return _run_by(rest, UV)


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


def _takes_a_descriptor(text: str, at: int) -> bool:
    """Whether the operator at `at` is a redirection a descriptor can be written against.

    One opening with `<` or `>`, and not a process substitution's `<(` or `>(`:
    bash 5.2.21 prints `2/dev/fd/63` for `echo 2>(cat)`, the `2` a word.
    """
    operator = _operator_at(text, at)
    if operator not in REDIRECTIONS or operator[0] not in "<>":
        return False
    return not (operator in ("<", ">") and text[at + 1 : at + 2] == "(")


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
        # Whether any of the word in progress was quoted or escaped, which
        # keeps a number written against a redirection a word.
        self.quoted = False
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
                    self.in_word = self.quoted = True
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
                self._end_word(redirected=_takes_a_descriptor(text, self.at))
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

    def _end_word(self, *, redirected: bool = False) -> None:
        """End the word in progress; `redirected` where a redirection follows it unspaced."""
        if not self.in_word:
            return
        word = "".join(self.word)
        # Unquoted, and not the delimiter a `<<` is waiting for, which takes
        # this word whatever follows it.
        descriptor = redirected and not self.quoted and self.introducer is None
        if descriptor and DESCRIPTOR.fullmatch(word):
            word = Descriptor(word)
        self.tokens.append(word)
        self.word.clear()
        self.in_word = self.quoted = False
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
        self.in_word = self.quoted = True
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
        self.in_word = self.quoted = True
        self.at = at + 1

    def _double_quoted(self) -> None:
        text = self.text
        at = self.at + 1
        while at < len(text):
            character = text[at]
            following = text[at + 1 : at + 2]
            if character == '"':
                self.in_word = self.quoted = True
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
