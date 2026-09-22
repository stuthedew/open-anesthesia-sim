#!/usr/bin/env bash
# PreToolUse hook on Bash: refuse a gate command whose exit status the command
# string throws away.
#
# A shell pipeline reports the status of its **last** stage. `make check 2>&1 |
# tail -45` therefore exits with `tail`'s status, and `tail` succeeds on any
# input, so a red tree arrives at the session as exit 0. Nothing in the harness
# distinguishes that from a green one: a non-zero exit is flagged, and an exit 0
# is not, so the one signal a session reads is the one the pipe replaced.
#
# `PL-2JRC` is what that costs. The session ran exactly that command, read exit
# 0, and reported `make check` green in the commit message and in the body of
# `#880`. The tree it pushed was red. The correction is the block that body now
# opens with, and `PL-D0W8` is this hook.
#
# **Prose could not have caught it, and the reason is specific rather than
# general.** The rule has to fire at the moment a command is written, which is
# not preceded by a read, so no path-scoped rule reaches it; and it has to fire
# inside exploration subagents, which carry none of the main session's resident
# context but do run these hooks. `permissionDecisionReason` is shown to the
# model (https://code.claude.com/docs/en/hooks, read 2026-09-16), so the
# refusal arrives at the one moment the wrong conclusion would have formed.
# `no-prune-guard.sh` beside this one made the same move out of ten resident
# lines (`PL-JK0M`); the resident set does not grow to pay for this one.
#
# **The remedy is one token, which is what keeps this from being routed
# around.** `set -o pipefail` makes a pipeline report its rightmost non-zero
# stage, so `tail` still trims the output and a red gate still arrives non-zero.
# The session keeps the short output it piped for - `CLAUDE.md` asks it to
# summarize rather than to load - and loses nothing. A guard whose remedy costs
# context would be a guard sessions learn to work around.
#
# **What counts as a gate is a list, not an inference.** The guarded commands
# are the ones whose exit status *is* the evidence a session reports:
# `make check|test|docket|doc-check|prebuild|pr-title`, `bin/docket
# check|verify`, `pytest`, `mypy`, `ruff`, and `tools/*_check.py`. Deciding by
# inference - anything that "looks like a check" - is the judgment half
# `CLAUDE.md` refuses to script, and a wrong guess here blocks a session. The
# `_check.py` suffix is the one pattern rather than a name, because 16 of
# `tools/`'s 22 scripts carry it and a check added later would otherwise arrive
# unguarded.
#
# **Guarding only `make check` was considered and refused.** It is the observed
# instance; the fault is that a verification command's status can be discarded,
# and `uv run pytest -q 2>&1 | tail -20` reproduces it one command down. The
# `Makefile`'s own `--no-cache` comment settles this shape of question the same
# way: a fix that "treats the instance rather than the fault" leaves the next
# spelling to find it again.
#
# **Narrow on purpose in the other direction.** A gate reached through a wrapper
# - `timeout 900 make check | tail`, `xargs make check` - is not matched, and
# neither is one built out of a variable. Both are unobserved here, and widening
# the pattern to reach them is how a guard starts refusing commands nobody
# meant it to. `uv run` is unwrapped because it is how this project spells most
# of the list.
#
# Fails open in every error path - no python3, an unreadable payload, a command
# it cannot tokenise, a `#` that truncates the parse - like the two guards
# beside it. A guard that breaks the session costs more than the round it saves.
set -uo pipefail

payload=$(cat)
command -v python3 >/dev/null 2>&1 || exit 0

PAYLOAD="$payload" python3 -c '
import json, os, re, shlex, sys

try:
    data = json.loads(os.environ["PAYLOAD"])
except (ValueError, KeyError):
    sys.exit(0)
if data.get("tool_name") != "Bash":
    sys.exit(0)
command = data.get("tool_input", {}).get("command")
if not isinstance(command, str):
    sys.exit(0)

# Only the text before the first heredoc introducer is a command; what follows
# is document content. This repository writes prose *about* the hazard through
# heredocs routinely - this hook, the item, the commit message that landed it -
# and blocking that would be the guard eating its own documentation.
command = command.split("<<", 1)[0]

# A newline separates two commands exactly as `;` does, and shlex would
# otherwise discard it as whitespace and read a two-line script as one segment.
# Substituting inside a quoted string is harmless: the string stays one token
# either way, so only the tokenizer sees the change.
command = command.replace("\n", " ; ")

# `punctuation_chars` is what makes `make check|tail` tokenise - plain
# `shlex.split` would return `check|tail` as one word and miss the pipe
# entirely. It also keeps a quoted argument whole, so the `|` inside
# `git commit -m "... | tail ..."` reads as the text it is. `commenters`
# stays at the default, so a trailing `# note` truncates the parse: that can
# only lose a separator, never invent one, which is the safe direction.
try:
    lexer = shlex.shlex(command, posix=True, punctuation_chars=True)
    lexer.whitespace_split = True
    tokens = list(lexer)
except ValueError:
    sys.exit(0)

SEPARATORS = {";", "&&", "||", "|", "&"}
ASSIGNMENT = re.compile(r"^[A-Za-z_]\w*=")
INTERPRETER = re.compile(r"^python(?:3(?:\.\d+)?)?$")
GROUPING = ("(", "{", "!")

MAKE_GATES = ("check", "test", "docket", "doc-check", "prebuild", "pr-title")
DOCKET_GATES = ("check", "verify")
DIRECT = ("pytest", "mypy", "ruff")


def base(token):
    return token.rsplit("/", 1)[-1]


def strip_prefixes(tokens):
    """Drop grouping, leading assignments and a `uv run` wrapper."""
    rest = list(tokens)
    while rest and rest[0] in GROUPING:
        rest.pop(0)
    while rest and ASSIGNMENT.match(rest[0]):
        rest.pop(0)
    if len(rest) >= 2 and base(rest[0]) == "uv" and rest[1] == "run":
        rest = rest[2:]
        while rest and ASSIGNMENT.match(rest[0]):
            rest.pop(0)
    return rest


def check_script(arguments):
    """The `tools/` check named in these arguments, or None."""
    for index, token in enumerate(arguments):
        if base(token).endswith("_check.py"):
            return token
        if base(token) == "dead_ends.py" and "check" in arguments[index + 1:]:
            return token + " check"
    return None


def gate(segment):
    """The gate command this segment invokes, spelled for the message, or None."""
    rest = strip_prefixes(segment)
    if not rest:
        return None
    head, arguments = rest[0], rest[1:]
    name = base(head)
    if name == "make":
        named = [a for a in arguments if a in MAKE_GATES]
        return "make " + named[0] if named else None
    if name == "docket" and arguments and arguments[0] in DOCKET_GATES:
        return head + " " + arguments[0]
    if name in DIRECT:
        return name
    if INTERPRETER.match(name):
        return check_script(arguments)
    if base(head).endswith("_check.py"):
        return head
    return None


def sets_pipefail(segment):
    """True for `set -o pipefail` in any of its spellings, false for `set +o`."""
    rest = list(segment)
    while rest and ASSIGNMENT.match(rest[0]):
        rest.pop(0)
    if not rest or rest[0] != "set" or "pipefail" not in rest[1:]:
        return False
    flag = rest[rest.index("pipefail") - 1]
    return flag.startswith("-") and flag.endswith("o")


segments, separators, current = [], [], []
for token in tokens:
    if token in SEPARATORS:
        segments.append(current)
        separators.append(token)
        current = []
    else:
        current.append(token)
segments.append(current)
separators.append(None)

offender = swallowed_by = None
for index, segment in enumerate(segments):
    name = gate(segment)
    if name is None:
        continue
    pipefail = any(sets_pipefail(s) for s in segments[:index])
    # Everything to the right decides whether this status survives. `&&` is the
    # one separator that propagates it - a failing gate short-circuits the rest
    # and the string exits non-zero. `|` propagates it only under pipefail. `;`
    # and `&` hand the status to whatever runs next, and `||` hands it to a
    # fallback that succeeds, which is the same loss wearing a different face.
    for separator in separators[index:]:
        if separator is None or separator == "&&":
            continue
        if separator == "|" and pipefail:
            continue
        offender, swallowed_by = name, separator
        break
    if offender is not None:
        break

if offender is None:
    sys.exit(0)

LOSS = {
    "|": (
        "A pipeline reports its LAST stage, and `tail`, `head`, `grep` and "
        "`tee` all succeed on any input"
    ),
    ";": "The status of whatever runs after the `;` is what the string exits with",
    "&": "The gate is backgrounded, so the string exits before it has an answer",
    "||": "The `||` fallback succeeds, so a failing gate still exits 0",
}

reason = (
    "This command runs `" + offender + "` and then throws its exit status "
    "away. " + LOSS.get(swallowed_by, "The status is discarded") + ", so a RED "
    "tree arrives here as exit 0 and nothing else in the output is read as a "
    "verdict.\n\n"
    "That is not hypothetical. `PL-2JRC` ran `make check 2>&1 | tail -45`, "
    "read exit 0, and reported the gate green in its commit message and in the "
    "body of `#880`. The tree it pushed was red, and the correction is the "
    "block that body now opens with. `PL-D0W8` is this refusal.\n\n"
    "Two spellings keep the status. The first is the one you want - the output "
    "is just as short:\n\n"
    "    set -o pipefail; " + offender + " 2>&1 | tail -45\n\n"
    "    " + offender + " > /tmp/gate.log 2>&1      # then read the file in a "
    "second call\n\n"
    "`set -o pipefail` makes a pipeline report its rightmost non-zero stage, "
    "so `tail` still trims the output and a red gate still exits non-zero. It "
    "is one token, it costs no context, and it is never wrong to add. `&&` "
    "also preserves the status, where the sequencing suits: "
    "`" + offender + " && tail -45 /tmp/gate.log`.\n\n"
    "Guarded because their exit status IS the evidence a session reports: "
    "`make check|test|docket|doc-check|prebuild|pr-title`, `bin/docket "
    "check|verify`, `pytest`, `mypy`, `ruff`, and `tools/*_check.py`. "
    "Everything else pipes freely - `bin/docket next | head -30` and `git log "
    "| head` are untouched.\n\n"
    "Do not answer this by dropping the pipe and reading the whole run. The "
    "output is thousands of tokens of passing checks, and keeping the session "
    "short is the largest adherence lever this project has."
)
sys.stdout.write(
    json.dumps(
        {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": reason,
            }
        }
    )
)
' 2>/dev/null || exit 0
