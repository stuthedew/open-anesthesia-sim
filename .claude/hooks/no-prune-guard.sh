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
# Four shapes delete remote-tracking refs, each a `git` command whose words
# include these in this order. Matched on the words because that is what the
# hook is handed; a shell that builds the flag from a variable is out of reach,
# and so is a command handed to another shell as a string (`bash -c "..."`),
# and neither is how any session has ever written it.
PRUNE_FLAGS = ("--prune", "--prune-tags", "-p")
PRUNE_SETTING = re.compile(r"\b(?:remote\.\S+\.prune|fetch\.prune)\b")
SHAPES = (
    ("fetch", PRUNE_FLAGS.__contains__),
    ("remote", "prune"),
    ("remote", "update", "--prune"),
    ("config", PRUNE_SETTING.search),
)


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
    words[0] == "git" and in_order(words[1:], shape)
    for words in shell_split.commands(command)
    for shape in SHAPES
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
    "To fetch without pruning, drop the flag: `git fetch origin`."
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
