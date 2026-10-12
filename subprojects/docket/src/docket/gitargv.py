"""Where a git call's command name stands: past git's own options, each with its value.

`git [-C <path>] [-c <name>=<value>] [--git-dir=<path>] ... <command> [<args>]`:
git reads its own options ahead of the command name, and some of them take the
next word as their value where no `=` joins one, so that word is never the
command. `docket.vcs` names each read by its command, and the Bash guards under
`.claude/hooks/` decide on a command before it runs; both read it here. `vcs`
stepped over a value only after `-c` and `-C` while `no-prune-guard.sh` and
`push-check-guard.sh` each held the full table, so `git --git-dir /x/.git log`
was the command `/x/.git` to docket and `log` to both guards (`PL-ZXCN`).

A leaf, importing nothing: each guard is a fresh `python3` on every Bash call,
and `tests/unit/test_shell_reader.py` holds what a guard's imports may load.
"""

#: The options git reads ahead of the command name that take the next word as
#: their value where no `=` joins one. From git 2.43.0's `git -h` and git.c's
#: `handle_options`, each measured on 2026-10-12 by running
#: `git <option> <value> rev-parse` outside a repository: every one ran
#: `rev-parse` after its value. `-C` and `-c` take only the next word; the rest
#: also take `=<value>`. `--exec-path` with no `=` prints the path and runs
#: nothing, and `--super-prefix` and `--list-cmds` are refused in this form.
TAKES_A_WORD = frozenset(
    ("-C", "-c", "--config-env", "--git-dir", "--work-tree", "--namespace", "--attr-source")
)


def own_options(args: list[str] | tuple[str, ...]) -> tuple[list[tuple[str, str]], int]:
    """git's own options at the head of `args`, each with its value, and where the command stands.

    `args` are the words after `git` itself. A value joined by `=` is split
    off; an option `TAKES_A_WORD` names, written bare, takes the next word.
    Where no command name follows, the index is at or past the end of `args`.
    """
    options: list[tuple[str, str]] = []
    at = 0
    while at < len(args) and args[at].startswith("-"):
        option, equals, value = args[at].partition("=")
        at += 1
        if option in TAKES_A_WORD and not equals:
            value = args[at] if at < len(args) else ""
            at += 1
        options.append((option, value))
    return options, at


def subcommand_of(args: list[str] | tuple[str, ...]) -> str:
    """The git command `args` name, past git's own options, or `""` where none follows.

    `claims.work_outside_queue` asked `-c core.quotePath=false log` first, and
    read as the command `core.quotePath=false` it was counted under that name
    and, being no read `vcs` knows, emptied `GitRunner`'s memo (`PL-N162`).
    `verify` and `tools/doc_check.py` name a read that failed by this rather
    than by `args[0]` for the same reason.
    """
    _, at = own_options(args)
    return args[at] if at < len(args) else ""


def is_git(words: list[str]) -> bool:
    """Whether a command's words run git, by name or by path.

    A path to git is git: `/usr/bin/git fetch --prune` prunes (`PL-TRMN`).
    """
    return bool(words) and words[0].rsplit("/", 1)[-1] == "git"
