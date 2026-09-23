---
id: PL-1SFZ
title: gate-status-guard.sh refuses a command that keeps pytest's status - set -o pipefail inside a { ...; } group followed by echo "exit=$?" - while a near-identical group passes, so a correct spelling costs a retry and teaches that the refusal can be wrong
status: untriaged
feature: gate-status-guard
added: 2026-09-23
---

**Problem.** gate-status-guard.sh refuses a command that keeps pytest's status - set -o pipefail inside a { ...; } group followed by echo "exit=$?" - while a near-identical group passes, so a correct spelling costs a retry and teaches that the refusal can be wrong

**Found 2026-09-23 while working `PL-KH3Q`.** Replayed through
`bash .claude/hooks/gate-status-guard.sh` with the Bash tool's JSON on stdin.
This shape is refused (`permissionDecision` on stdout), and it keeps the
status: `pipefail` is set before the gate, and the segment after the pipeline
reads `$?`.

    cd /r && git status -s && git stash -q && { set -o pipefail; uv run pytest -q -p no:randomly t.py -k "name" 2>&1 | tail -12; echo "exit=$?"; }; git stash pop -q && git status -s

This one passes:

    cd /x && git stash -q && { set -o pipefail; uv run pytest -q t.py 2>&1 | tail -12; echo "exit=$?"; }; git stash pop -q

Removing any single one of the differences still refuses: the leading
`git status -s &&`, `-p no:randomly`, `-k "name"`, or the trailing
`git stash pop -q && git status -s`. So the trigger is a combination, not yet
isolated. Start from those two strings. `sets_pipefail` and the separator
walk after it (around line 171 and line 198) are where the verdict is made.
