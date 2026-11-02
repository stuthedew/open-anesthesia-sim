#!/usr/bin/env bash
# PreToolUse hook on every MCP tool: refuse a call that would publish an email
# address on GitHub in a title or a body (`PL-7K31`).
#
# A body is public as soon as GitHub has it. Removing an address later leaves
# it in the description's edit history, and the squash merge copies the body
# into `main`'s history. So the only point at which the address can be kept out
# is before the call. `#1480` opened with the owner's address on 2026-10-17.
#
# **Which calls it reads** (`PL-NZJG`). The GitHub server owns its tool names
# and changes them without notice. It has already folded its issue tools into
# one `issue_write`. A matcher naming `create_pull_request` and
# `update_pull_request` would stop this guard silently after such a change. So
# `.claude/settings.json` wires it on `^mcp__.*$`, and `screen` reads every call
# that names a repository by `owner` and `repo` and carries a `title` or a
# `body`. That covers a pull request, an issue, a comment and a review, whatever
# the tool is called. A call that names no repository, such as a Projects
# thread's post or an email, is not read. What goes unchecked is GitHub text
# sent in a field with another name, or by a call that names its repository
# another way. `.claude/rules/apparatus-standard.md` § "The floor" has the rule,
# in its paragraph on a guard keyed on names that another system owns.
#
# The rule is `screen` in `tools/pr_body_check.py`, which recovers the bodies
# this guard protects. This script is only the entry point, kept here so that
# what `.claude/settings.json` runs stays in the protected directory, as
# `docs/apparatus.md` § "Wired hooks (`.claude/hooks/`)" explains.
#
# **A pull request call it lets through gets a note** beside the call's
# result, as `additionalContext`: read the published body back, and the
# `pull-request` skill has the rest. The server can rewrite a body and still
# return success, and `PL-SN2Z` found that a moment arriving in the middle of a
# task needs a hook to name it (`PL-S2NL`). `read_back` in the same file decides
# which calls get it: those whose tool name contains `pull_request` and that
# carry a title or a body, except the review tools it names. A pull request tool
# renamed without `pull_request` in its name gets no note, and nothing is
# refused for that.
#
# **Fails open, like the Bash guards.** A payload `screen` cannot read is let
# through, and so is a python3 that is missing or fails, which prints nothing,
# since a false refusal blocks correct work.
set -uo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
python3 "$root/tools/pr_body_check.py" --screen || true
exit 0
