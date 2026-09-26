#!/usr/bin/env bash
# PreToolUse hook on Bash: refuse a git call that would prune remote refs.
#
# A stale `origin/<branch>` ref can be the only surviving copy of an item
# captured on a branch nobody merged. That is why `docket.vcs.fetch_remote`
# fetches without `--prune`, and what `bin/docket stranded` exists to recover;
# `PL-HKF4` came within one prune of losing exactly that.
#
# **This used to be ten lines of `CLAUDE.md`, resident in every session**
# (`PL-JK0M`). A prohibition on a command string is decidable by reading the
# command, so it belongs in a check rather than in prose every session carries
# before it has read anything - `CLAUDE.md`'s own first routing disposition.
# The prose fired only if the session remembered it; this fires always.
#
# **The deny message carries the recipe, because this is the moment it is
# wanted.** A session reaching for `--prune` is usually trying to restart a
# branch whose pull request merged, and the safe form of that is three
# commands rather than a prune. Answering the question the caller actually had
# is what makes a refusal cheaper than the prose was.
#
# Fails open in every error path - no python3, an unreadable payload,
# `shell_split.py` missing from beside it - because a guard that breaks the
# session costs more than the ref it protects. `docs/resident-instructions.md`
# records the trade. A command bash would refuse is not one of them: bash runs
# every line before the one it cannot finish, so the lines before it are read.
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

# Where each command starts is the answer `shell_split.py` gives, which the
# three Bash guards share (`PL-PVW2`), and this guard reads every command it
# finds: those in a subshell or a `$( )` too, quoted or not, since each runs. A
# quoted argument stays one word, so a `;` or a flag inside it is the text it
# is, where the regex this file used took a `;` inside quotes for a separator
# (`PL-WGFY`). Heredoc bodies and comments are gone, which is what lets this
# repository write prose *about* pruning - `CLAUDE.md`, this hook, the ledger -
# without the guard eating its own documentation; a prune after the terminator
# of a heredoc is read like any other line (`PL-39LD`).
#
# **What prunes is read from git 2.43 itself** (`PL-R17X`): its usage lines,
# `git -h`, `git fetch -h`, `git pull -h` and `git remote -h`, and each
# spelling run against a scratch remote, the one way to learn which spellings
# delete a ref rather than which ones say they might. Two readings:
#
# - A setting passed ahead of the command name, as `-c <name>=<value>` or
#   `--config-env=<name>=<envvar>`, holds for the whole call. A prune setting
#   there prunes unless its value reads as false, and one written with no `=`
#   reads as true. The value `--config-env` names sits in the environment, out
#   of sight, so that setting is refused whatever it holds, and either is
#   refused whatever command follows. There `-p` and `-P` are --paginate and
#   --no-pager, and a `-c` after the command name is an option of that command
#   (`git grep -c` counts), so only the options git reads as its own are
#   read, stepping over each value a word of its own carries.
# - Five shapes delete refs, each a `git` command whose words include these in
#   this order. `fetch`, `pull` and `remote update` prune on a flag, spelled
#   long or as a letter among bundled short flags - `-tp` is `-t -p` - up to
#   the first letter taking a value, which takes the rest of the word: `-j4p`
#   is jobs `4p`, an error, and prunes nothing. `remote prune` always prunes,
#   and `config` writes a setting every later fetch reads.
#
# `--prune-tags`, `-P` and the `pruneTags` settings delete tags, and only where
# pruning is on, which a config file this hook never reads may have turned on,
# so they are refused beside the flags that turn it on.
#
# Matched on the words because that is what the hook is handed. Out of reach:
# an alias; a setting passed in `GIT_CONFIG_PARAMETERS` or `GIT_CONFIG_COUNT`;
# an abbreviated long option, though `git pull --pru` prunes; a shell that
# builds the flag from a variable; and a command handed to another shell as a
# string (`bash -c "..."`). None is how any session has written it.
TAKES_A_WORD = frozenset(
    ("-C", "-c", "--config-env", "--git-dir", "--work-tree", "--namespace", "--attr-source")
)
PRUNE_SETTING = re.compile(r"\b(?:fetch|remote\.\S+)\.prune(?:tags)?\b", re.IGNORECASE)
FALSE = frozenset(("", "false", "no", "off", "0"))


def flag(long_forms, prune, value):
    """A test for one word: a long form, or a bundle holding a letter in `prune` before any in `value`."""

    def prunes(word):
        if word in long_forms:
            return True
        if word.startswith("--") or not word.startswith("-"):
            return False
        for letter in word[1:]:
            if letter in value:
                return False
            if letter in prune:
                return True
        return False

    return prunes


SHAPES = (
    ("fetch", flag(("--prune", "--prune-tags"), "pP", "jo")),
    ("pull", flag(("--prune",), "p", "rsXSjo")),
    ("remote", "prune"),
    ("remote", "update", flag(("--prune",), "p", "")),
    ("config", PRUNE_SETTING.search),
)


def sets_pruning(words):
    """Whether the options git reads ahead of the command name pass a prune setting."""
    at = 1
    while at < len(words) and words[at].startswith("-"):
        option, equals, value = words[at].partition("=")
        at += 1
        if option in TAKES_A_WORD and not equals:
            value = words[at] if at < len(words) else ""
            at += 1
        name, equals, setting = value.partition("=")
        if not PRUNE_SETTING.fullmatch(name):
            continue
        if option == "--config-env":
            return True
        if option == "-c" and not (equals and setting.lower() in FALSE):
            return True
    return False


def in_order(words, steps):
    """Whether `words` holds a word for each step, in order: one equal to it, or passing it."""
    at = 0
    for step in steps:
        passes = step if callable(step) else step.__eq__
        while at < len(words) and not passes(words[at]):
            at += 1
        if at == len(words):
            return False
        at += 1
    return True


if not any(
    words[0] == "git"
    and (sets_pruning(words) or any(in_order(words[1:], shape) for shape in SHAPES))
    for words in shell_split.commands(command)
):
    sys.exit(0)

reason = (
    "Pruning remote-tracking refs is refused in this repository. A stale "
    "`origin/<branch>` ref can be the only surviving copy of an item captured "
    "on a branch nobody merged (`PL-HKF4` came within one prune of losing "
    "one), so `docket.vcs.fetch_remote` fetches without `--prune` and "
    "`bin/docket stranded` recovers what such a ref holds.\n\n"
    "Run `bin/docket stranded` first: it prints every item that exists only on "
    "a branch, with the `git checkout` line that restores the file.\n\n"
    "To restart a branch whose pull request has already merged, delete just "
    "that one ref and rebase the name onto the merged base:\n\n"
    "    git branch -dr origin/<branch>\n"
    "    git fetch origin main\n"
    "    git checkout -B <branch> origin/main\n\n"
    "To fetch without pruning, drop the flag or the setting: `git fetch origin`."
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
