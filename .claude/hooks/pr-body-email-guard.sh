#!/usr/bin/env bash
# PreToolUse hook on the GitHub server's pull request tools: refuse a
# `create_pull_request` or `update_pull_request` call whose title or body holds
# an email address (`PL-7K31`).
#
# A body is public as soon as GitHub has it. Removing an address later leaves
# it in the description's edit history, and the squash merge copies the body
# into `main`'s history. So the only point at which the address can be kept out
# is before the call. `#1480` opened with the owner's address on 2026-10-17.
#
# The rule is `screen` in `tools/pr_body_check.py`, which recovers the bodies
# this guard protects. This script is only the entry point, kept here so that
# what `.claude/settings.json` runs stays in the protected directory, as
# `docs/apparatus.md` § "Wired hooks (`.claude/hooks/`)" explains.
#
# **Fails open, like the Bash guards.** A payload `screen` cannot read is let
# through, and so is a python3 that is missing or fails, since a false refusal
# blocks correct work and the matcher has already chosen these calls.
set -uo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
python3 "$root/tools/pr_body_check.py" --screen || true
exit 0
