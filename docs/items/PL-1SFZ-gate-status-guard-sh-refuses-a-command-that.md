---
id: PL-1SFZ
title: gate-status-guard.sh refuses a command that keeps pytest's status - set -o pipefail inside a { ...; } group followed by echo "exit=$?" - while a near-identical group passes, so a correct spelling costs a retry and teaches that the refusal can be wrong
priority: P3
effort: S
status: ready
classes: defect
feature: gate-status-guard
touches: .claude/hooks/gate-status-guard.sh, tests/unit/test_gate_status_guard.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the second 2026-09-23 triage pass
added: 2026-09-23
payoff: a pipefail command spelt correctly inside a group runs first time, and the guard's refusals stay ones a session obeys rather than learns to doubt
verify: grep -q 'def test_pipefail_set_inside_a_group_keeps_the_status' tests/unit/test_gate_status_guard.py
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

**Reproduced at triage, 2026-09-23, and the premise above is half wrong.** Both
commands quoted above are refused today, the second as well as the first, and
the hook has not changed since `630b915d` (2026-09-21). The trigger is one
token, not a combination: `sets_pipefail` reads a segment's first word as the
command without stripping the `{` or `(` that `strip_prefixes` strips for
`gate`, so a `set -o pipefail` that opens a group never counts. Replayed: `{ set
-o pipefail; uv run pytest -q t.py 2>&1 | tail -12; }` and the same inside `(
... )` are refused; `set -o pipefail; { uv run pytest -q t.py 2>&1 | tail -12;
echo "exit=$?"; }` passes.

**Why it matters.** The refusal tells the session to add `set -o pipefail`,
which the refused command already carries, so the correct spelling costs a retry
and the guard teaches that its refusals can be wrong - the lesson that gets a
guard routed around.

**Done when.** A `set -o pipefail` opening a `{ ...; }` or `( ... )` group
counts for the pipelines after it, as it does in bash, pinned by a test that
replays both group spellings.

**Generator check.** One-off: two readers of a segment's head disagree about
which prefixes to strip inside one hook. `PL-GVFC` is the same kind of fault in
the other command-parsing hook - each hook tokenises a command by its own rules
- but two items sharing no function are not a generator.
