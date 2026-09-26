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
# **Reading `$?` counts as keeping the status, and the first live firing is why.**
# It refused `make check > /tmp/gate.log 2>&1; echo "exit=$?"` on the `;`, which
# is correct by the separator and wrong about the command: that `echo` *is* the
# reader, and it puts the verdict in the output in words rather than in an exit
# code. `CLAUDE.md` retires a check that fires without changing a decision, so
# the exemption is the fix rather than a concession - restricted to the segment
# immediately after the separator, since anything in between replaces `$?` with
# its own status, and never after `&`, where `$?` is the background launch.
#
# **A group is read the way bash runs it, and a false refusal is why.** `{ set
# -o pipefail; uv run pytest -q t.py 2>&1 | tail -12; }` keeps the status and
# was refused twice over (`PL-1SFZ`): the `{` hid the `set` from the one reader
# of a segment's head that did not strip it, and the `;` that ends the group
# read as handing the status on. The scoping is bash's and not a looser one,
# because crediting a `set` to everything after it would pass `(set -o
# pipefail; make check) | tail`, where the `set` dies with its subshell and the
# outer pipe loses the status exactly as `PL-2JRC`'s did.
#
# **An `if` or a loop is read the way bash runs it too, once the gate inside is
# visible** (`PL-0X0G`). Until then a reserved word read as the command's name,
# so `for f in a; do make check | tail; done` and `time make check | tail`
# passed as commands named `do` and `time`. Seen, a gate ending an `if` branch
# leaves with the `if`, whose status is the last command it ran (`help if`); a
# gate ending the test of an `if`, `while` or `until` is read by it, as `$?`
# is; and a gate ending a loop body is refused, because the next pass replaces
# its status and a red pass before a green one exits 0 (`help for`). Each is a
# group for `pipefail` as `{ }` is, and the walk steps over one whole after a
# `&&`: in `make check && if true; then echo; fi; git status` the `then` reads
# `true`, and the `;` after `fi` loses the gate's status.
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
# **Where one command ends is `shell_split.py`'s answer, not this file's.** The
# three Bash guards import it, so a shape one of them read differently from bash
# - a `)` glued to the `;` after it (`PL-63TT`), a backslash-newline
# (`PL-R5RF`), a command after a heredoc's terminator (`PL-39LD`) - is read
# right by all three at once (`PL-PVW2`). It keeps a quoted argument whole, so
# the `|` inside `git commit -m "... | tail ..."` reads as the text it is, and
# it removes a heredoc's body, which is document content: this repository writes
# prose *about* the hazard through heredocs routinely, and blocking that would be
# the guard eating its own documentation.
#
# Fails open in every error path - no python3, an unreadable payload, a command
# bash itself would refuse, `shell_split.py` missing from beside it - like the
# two guards beside it. A guard that breaks the session costs more than the
# round it saves.
set -uo pipefail

payload=$(cat)
command -v python3 >/dev/null 2>&1 || exit 0
hooks=$(dirname "${BASH_SOURCE[0]}")

PAYLOAD="$payload" HOOKS="$hooks" python3 -c '
import json, os, re, sys

sys.path.insert(0, os.environ["HOOKS"])
import shell_split

try:
    data = json.loads(os.environ["PAYLOAD"])
except (ValueError, KeyError):
    sys.exit(0)
if data.get("tool_name") != "Bash":
    sys.exit(0)
command = data.get("tool_input", {}).get("command")
if not isinstance(command, str):
    sys.exit(0)

cut = shell_split.segments(command)
if cut is None:
    sys.exit(0)

INTERPRETER = re.compile(r"^python(?:3(?:\.\d+)?)?$")
# A compound command runs in this shell, as a `{ }` group does, unless it is
# piped or backgrounded. `case` is not read: the splitter reads the `)` after
# each of its patterns as a subshell closing.
COMPOUND = ("if", "while", "until", "for", "select")
# The words that end a group, and every group end a command can start after.
ENDS = ("}", "fi", "done")
CLOSERS = (")",) + ENDS

MAKE_GATES = ("check", "test", "docket", "doc-check", "prebuild", "pr-title")
DOCKET_GATES = ("check", "verify")
DIRECT = ("pytest", "mypy", "ruff")


def base(token):
    return token.rsplit("/", 1)[-1]


def strip_prefixes(tokens):
    """Drop grouping, leading assignments and a `uv run` wrapper.

    `gate` and `sets_pipefail` both read a segment head through
    `shell_split.command_words`, so they cannot disagree about where its
    command starts - which they did, and a `set` opening a group went unseen
    (`PL-1SFZ`).
    """
    rest = shell_split.command_words(tokens)
    if len(rest) >= 2 and base(rest[0]) == "uv" and rest[1] == "run":
        rest = rest[2:]
        while rest and shell_split.ASSIGNMENT.match(rest[0]):
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
    rest = shell_split.command_words(segment)
    if not rest or rest[0] != "set" or "pipefail" not in rest[1:]:
        return False
    flag = rest[rest.index("pipefail") - 1]
    return flag.startswith("-") and flag.endswith("o")


def pipefail_by_separator(segments, separators):
    """Whether `pipefail` holds in the shell that runs each separator, and how deep it is.

    A `set` lasts as long as the shell it runs in. `( ... )` and a
    substitution are subshells, and so is a command, `{ ...; }` group, `if`
    or loop that is piped or backgrounded, so a `set` inside one ends where it
    does. A group, `if` or loop run on its own is this shell, and its `set`
    outlives it.

    The depth is how many groups, `if`s and loops are open at each separator,
    which is where the walk below reads one of them ending.
    """
    state, groups, held, depth = False, [], [], []
    for index, segment in enumerate(segments):
        piped = index > 0 and separators[index - 1] == "|"
        forked = separators[index] in ("|", "&")
        rest = shell_split.command_words(segment)
        opened = segment[: len(segment) - len(rest)]
        # `for` and `select` open a loop with a name after them, not a command.
        opened += rest[:1] if rest[:1] in (["for"], ["select"]) else []
        for opener in opened:
            if opener in ("(", "{") or opener in COMPOUND:
                # A group takes the pipe into it; its first command does not.
                groups.append((state, opener == "(" or piped))
                piped = False
        if sets_pipefail(rest) and not piped and not forked:
            state = True
        for position, token in enumerate(rest):
            # A `(` or `)` the splitter read as an operator; a quoted one is a word.
            if isinstance(token, shell_split.Operator):
                if token == "(":
                    groups.append((state, True))
                elif token == ")" and groups:
                    state = groups.pop()[0]
            # `}`, `fi` and `done` are words, and end a group only where a
            # command could start.
            elif token in ENDS and groups and (position == 0 or rest[position - 1] in CLOSERS):
                before, subshell = groups.pop()
                if subshell or forked:
                    state = before
        held.append(state)
        depth.append(len(groups))
    return held, depth


segments = [words for words, _ in cut]
separators = [separator for _, separator in cut]
pipefail, depth = pipefail_by_separator(segments, separators)


def ends(start, deepest):
    """The first segment from `start` that leaves `deepest` or fewer groups open, or None.

    That is where a command opening an `if`, a loop or a group finishes, past
    the separators of its own that the walk would otherwise read as the next.
    None is a construct bash would refuse as unfinished.
    """
    for index in range(start, len(segments)):
        if depth[index] <= deepest:
            return index
    return None


offender = swallowed_by = None
for index, segment in enumerate(segments):
    name = gate(segment)
    if name is None:
        continue
    # Everything to the right decides whether this status survives. `&&` is the
    # one separator that propagates it - a failing gate short-circuits the rest
    # and the string exits non-zero. `|` propagates it only under pipefail, in
    # the shell that runs that pipe. `;` and `&` hand the status to whatever
    # runs next, and `||` hands it to a fallback that succeeds, which is the
    # same loss wearing a different face.
    lost = None
    at = index
    while at < len(segments):
        separator = separators[at]
        following = at + 1
        after = segments[following] if following < len(segments) else []
        if separator is None:
            break
        if separator == "&&" or (separator == "|" and pipefail[at]):
            # The status travels to the end of the next command, and an `if`,
            # a loop or a group ends only where it closes: in `make check &&
            # if true; then echo; fi; git status` the `;` after `true` belongs
            # to the `if`, and the one after `fi` loses the status.
            end = ends(following, depth[at])
            if end is None:
                break
            at = end
            continue
        if separator == ";":
            # A `;` before the `}` or `)` that ends a group hands the status to
            # nothing: the group exits with it, and the separator after the
            # group decides the rest. `{ make check; }` keeps it; `{ make
            # check; } | tail` loses it at the `|`. An `if` exits with the last
            # command it ran (`help if`), so its `fi` is read the same way.
            if after[:1] in ([")"], ["}"], ["fi"]):
                at = following
                continue
            # Once a branch has run, the rest of its `if` does not, so the
            # status leaves at the `fi` that ends it. An `if` with no `fi` is
            # one bash refuses, and the guard fails open on it as on any other.
            if after[:1] in (["else"], ["elif"]):
                end = ends(following, depth[at] - 1)
                if end is None:
                    break
                at = end
                continue
            # A gate ending the test of an `if`, `while` or `until` is read by
            # it, as `$?` is below: the construct branches on the verdict.
            if after[:1] in (["then"], ["do"]):
                break
            # A gate ending a loop body is not, because the next pass replaces
            # its status and only the last pass reaches the exit (`help for`,
            # `help while`): a red pass before a green one exits 0.
            if after[:1] == ["done"]:
                lost = "done"
                break
        # Unless the next thing the string does is *read* the status. `make
        # check > /tmp/gate.log 2>&1; echo "exit=$?"` prints the verdict into
        # the output, which is the same guarantee the exit code gives and a
        # plainer one; `s=$?` captures it into a variable. Either way the
        # status has survived and the walk is over; what runs after a capture
        # is not this hook to police. Only the segment immediately after this
        # separator counts, because anything in between replaces `$?` with its
        # own status, and `&` is excluded outright: after a background launch
        # `$?` is the launch, never the gate.
        if separator != "&" and any("$?" in token for token in after):
            break
        lost = separator
        break
    if lost is not None:
        offender, swallowed_by = name, lost
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
    "done": (
        "The next pass of the loop replaces its status, and only the last pass "
        "reaches the exit"
    ),
}

# A refusal of a command that visibly sets `pipefail` reads as the guard being
# wrong - the lesson `PL-1SFZ` was filed against - so it says why this one is
# right.
UNREACHED = (
    "The command does set `pipefail`, but not in the shell that runs this "
    "pipe. A `set` lasts as long as the shell it runs in: inside `( ... )`, or "
    "inside a `{ ...; }` group, `if` or loop that is piped or backgrounded, it "
    "ends with the group, and after the pipeline it comes too late.\n\n"
)
unreached = swallowed_by == "|" and any(sets_pipefail(s) for s in segments)

# The spellings below keep one pass of a loop, so a loop is told how to keep
# every pass.
LOOPED = (
    "Inside a loop, read the status on every pass, before `done` - `"
    + offender
    + "; echo \"exit=$?\"; done` prints each verdict - or run the gate once "
    "over all its targets.\n\n"
)

reason = (
    "This command runs `" + offender + "` and then throws its exit status "
    "away. " + LOSS.get(swallowed_by, "The status is discarded") + ", so a RED "
    "tree arrives here as exit 0 and nothing else in the output is read as a "
    "verdict.\n\n"
    + (UNREACHED if unreached else "")
    + (LOOPED if swallowed_by == "done" else "")
    + "That is not hypothetical. `PL-2JRC` ran `make check 2>&1 | tail -45`, "
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
    "is one token, it costs no context, and it is never wrong to add. Two more "
    "spellings are accepted, where the sequencing suits: `&&`, which "
    "short-circuits on failure (`" + offender + " && tail -45 /tmp/gate.log`), "
    "and reading the status straight out into the output "
    "(`" + offender + " > /tmp/gate.log 2>&1; echo \"exit=$?\"`).\n\n"
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
