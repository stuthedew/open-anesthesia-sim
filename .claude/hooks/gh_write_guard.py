"""PreToolUse hook on Bash: refuse a `gh` call that could change anything on GitHub.

**Why** (`PL-3986`, `PL-1ZZ0`). `gh` is installed in the cloud container with
`GH_TOKEN` set, so `gh pr merge`, `gh api .../merge` and `gh pr create --body`
reach the actions that the merge guard and the email guard exist to check, and neither guard reads a Bash call. Teaching each guard
`gh`'s commands would add one more reader of a grammar GitHub owns and
extends, which is how the guards came to judge a request by its spelling
rather than its action. So a session changes GitHub through the GitHub MCP
tools alone, where both guards read every call, and this hook refuses each
`gh` call it cannot show to be a read. The harness hands a session `gh` for
searching only.

**What a read is.** `READS` names each `gh` command that only reads GitHub,
or only writes to this machine, as `gh pr checkout` does. `gh api` is a read
when its method is GET or HEAD and its endpoint is not `graphql`. As `gh`
2.89.0 decides, a call with no `--method` is a GET unless it sends a field or
an input file, which makes it a POST. Anything else is refused: another
command, an action the table does not name, an option ahead of the command,
and a method or command the shell builds from a variable. Under `xargs`,
which adds words this hook cannot see, a `gh api` call is refused too. A
`--help` or `-h` anywhere is a read, since `gh` then prints help and sends
nothing.

**Every `gh` the shell runs is read**, wherever `shell_split.commands` finds
one: after `&&`, in a pipe or a subshell, inside `$( )`, behind a wrapper such
as `timeout` or `env`, and named by its path.

**Fails closed on `gh`, unlike the Bash guards that read a command's words.**
Where `judge` cannot judge a call, because it raised an error or ran past its
deadline, `guard.py` asks `unjudged`, which refuses the call only if one of
its words is `gh` or ends in `/gh` (`PL-9KSJ`). A broken guard then costs a
`gh` call a retry, and lets nothing through to GitHub unread. Where this
module itself will not load, or `python3` will not start, the call goes
through with a note that nothing checked it, as it did before `guard.py`.

**What goes unread.** `gh` named through a variable, an alias or a function;
`gh` run by a script, by `bash -c` or by a wrapper `shell_split.py` does not
read; and any other client that carries the token, such as `curl` with
`$GH_TOKEN` or Python's `urllib`. Each is a known gap, recorded here rather
than read, because none is a spelling of `gh` a session writes by accident.

Standard library only, beside the shell reader the Bash guards share.
"""

from __future__ import annotations

import hook_input

#: The guard's name in the refusal log.
GH_GUARD = "gh-write-guard"

#: Each `gh` command that only reads, with the actions of it that only read.
#: `None` means every action is a read. Read from `gh help` in gh 2.89.0 on
#: 2026-11-03: `pr checkout`, `repo clone` and each `download` write only to
#: this machine.
READS: dict[str, frozenset[str] | None] = {
    "search": None,
    "status": None,
    "browse": None,
    "version": None,
    "help": None,
    "auth": frozenset({"status"}),
    "pr": frozenset({"view", "list", "diff", "checks", "status", "checkout"}),
    "issue": frozenset({"view", "list", "status"}),
    "run": frozenset({"view", "list", "watch", "download"}),
    "repo": frozenset({"view", "list", "clone"}),
    "release": frozenset({"view", "list", "download"}),
    "workflow": frozenset({"view", "list"}),
    "label": frozenset({"list"}),
    "gist": frozenset({"view", "list"}),
    "cache": frozenset({"list"}),
    "ruleset": frozenset({"view", "list", "check"}),
    "secret": frozenset({"list"}),
    "variable": frozenset({"list", "get"}),
    "org": frozenset({"list"}),
    "alias": frozenset({"list"}),
    "config": frozenset({"get", "list"}),
    "extension": frozenset({"list"}),
}

#: The options of `gh api` that take the next word as their value.
API_VALUE_OPTIONS = frozenset(
    {
        "-X",
        "--method",
        "-H",
        "--header",
        "-f",
        "--raw-field",
        "-F",
        "--field",
        "--input",
        "-q",
        "--jq",
        "-t",
        "--template",
        "--hostname",
        "-p",
        "--preview",
        "--cache",
    }
)

#: The options of `gh api` that send a request body, which makes a call with no
#: `--method` a POST.
API_BODY_OPTIONS = frozenset({"-f", "--raw-field", "-F", "--field", "--input"})

#: The methods of `gh api` that read.
READ_METHODS = frozenset({"GET", "HEAD"})

#: The characters that end a word in a command's text, for a call this hook
#: could not read: a separator, a pipe, a subshell, a substitution or a quote.
WORD_ENDS = str.maketrans({character: " " for character in ";|&()`$'\"<>"})

REMEDY = (
    "This repository sends every change to GitHub through the GitHub MCP tools, where "
    "`direct-merge-guard.sh` judges a merge and `pr-body-email-guard.sh` screens every field "
    "for an email address. Neither reads a Bash call, so `gh` is kept to reads (`PL-3986`). "
    "Use the MCP tool that does the same thing, such as `merge_pull_request`, "
    "`create_pull_request`, `update_pull_request` or `add_issue_comment`. Reads stay open: "
    "`gh search`, `gh pr view`, `gh run list`, and `gh api` with GET, such as "
    "`gh api -X GET search/code -f q='<terms>'`."
)


def _api_reads(arguments: list[str], under_xargs: bool) -> bool:
    """Whether `gh api` with `arguments` only reads, as the module docstring says."""
    import shell_split

    if under_xargs:
        return False
    method: str | None = None
    sends_body = False
    endpoint: str | None = None
    at = 0
    while at < len(arguments):
        word = arguments[at]
        name, value = word, ""
        if word.startswith("--") and "=" in word:
            name, value = word.split("=", 1)
        elif word[:2] in ("-X", "-f", "-F") and len(word) > 2:
            name, value = word[:2], word[2:]
        elif word in API_VALUE_OPTIONS:
            value = arguments[at + 1] if at + 1 < len(arguments) else ""
            at += 1
        elif not word.startswith("-") and endpoint is None:
            endpoint = word
        if name in ("-X", "--method"):
            method = value
        if name in API_BODY_OPTIONS:
            sends_body = True
        at += 1
    if method is None:
        method = "POST" if sends_body else "GET"
    if endpoint is None or endpoint == "graphql" or shell_split.EXPANDS.search(method):
        return False
    return method.upper() in READ_METHODS


def reads(words: list[str], under_xargs: bool = False) -> bool:
    """Whether the `gh` call `words`, from the program's own name on, only reads GitHub."""
    arguments = words[1:]
    if not arguments or any(word in ("--help", "-h") for word in arguments):
        return True
    if arguments[0] == "--version":
        return len(arguments) == 1
    command = arguments[0]
    if command == "api":
        return _api_reads(arguments[1:], under_xargs)
    if command not in READS:
        return False
    actions = READS[command]
    if actions is None:
        return True
    return len(arguments) > 1 and arguments[1] in actions


def judge(payload: str) -> str | None:
    """The refusal for a Bash call that runs a `gh` command that could write, or `None`."""
    import shell_split  # here, so a reader that fails to load is caught as an error

    # isort: split
    from docket.shell import basename  # on the path once `shell_split` has loaded

    call = hook_input.bash_call(payload)
    if call is None:
        return None
    refused = [
        command
        for command in shell_split.commands(call.command)
        if basename(command[0]) == "gh" and not reads(list(command), "xargs" in command.wrappers)
    ]
    if not refused:
        return None
    shown = "; ".join("`" + " ".join(command) + "`" for command in refused)
    reason = f"Refused: {shown} may change something on GitHub.\n\n{REMEDY}"
    return hook_input.deny(GH_GUARD, "gh-write", reason, payload)


def names_gh(command: str) -> bool:
    """Whether a word of `command`'s text is `gh`, or a path that ends in `/gh`."""
    return any(
        word == "gh" or word.endswith("/gh") for word in command.translate(WORD_ENDS).split()
    )


def decide(payload: str) -> str:
    """The hook output for a Bash call: `judge`'s refusal, or "" to let it through.

    `.claude/hooks/guard.py` runs this as the `gh-write-guard` before every
    Bash call (`PL-9KSJ`).
    """
    return judge(payload) or ""


def unjudged(payload: str, why: str) -> str | None:
    """The reason to refuse a call `judge` could not judge, where its text names `gh`.

    `why` says what stopped `judge`. `guard.py` asks this and logs the
    refusal. A call that names no `gh` returns `None`, so it goes through
    with a note instead.
    """
    call = hook_input.bash_call(payload)
    if call is None or not names_gh(call.command):
        return None
    return (
        f"Refused: the gh-write-guard hook could not read the command ({why}), "
        f"and the command names `gh`, which may change something on GitHub.\n\n{REMEDY}"
    )
