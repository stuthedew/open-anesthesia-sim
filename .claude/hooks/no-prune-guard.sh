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
# Fails open in every error path - no python3, an unreadable payload, a
# malformed command - because a guard that breaks the session costs more than
# the ref it protects. `docs/resident-instructions.md` records the trade.
set -uo pipefail

payload=$(cat)
command -v python3 >/dev/null 2>&1 || exit 0

PAYLOAD="$payload" python3 -c '
import json, os, re, sys

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
# is document content, and this repository writes prose *about* pruning through
# heredocs routinely - CLAUDE.md, this hook, the ledger. Blocking a session
# from writing the word would be the guard eating its own documentation.
command = command.split("<<", 1)[0]

# Four shapes delete remote-tracking refs, and nothing else in git does it as a
# side effect. Each is anchored at a command position - the start of the string
# or just after a shell separator - so the flag quoted inside an argument reads
# as the text it is. Matched on the command text because that is what the hook
# is handed; a shell that builds the flag from a variable is out of reach, and
# is not how any session has ever written it.
HEAD = r"(?:^|[;&|\n(])\s*(?:[A-Za-z_]\w*=\S*\s+)*"
PRUNING = (
    re.compile(HEAD + r"git\b[^|;&]*\bfetch\b[^|;&]*(?:--prune-tags\b|--prune\b|(?<![-\w])-p(?![\w]))"),
    re.compile(HEAD + r"git\b[^|;&]*\bremote\b[^|;&]*\bprune\b"),
    re.compile(HEAD + r"git\b[^|;&]*\bremote\b[^|;&]*\bupdate\b[^|;&]*--prune\b"),
    re.compile(HEAD + r"git\b[^|;&]*\bconfig\b[^|;&]*\b(?:remote\.\S+\.prune|fetch\.prune)\b"),
)
if not any(pattern.search(command) for pattern in PRUNING):
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
