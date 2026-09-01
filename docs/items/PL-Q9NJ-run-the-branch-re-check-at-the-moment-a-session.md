---
id: PL-Q9NJ
title: Run the branch re-check at the moment a session starts editing, not only when it asks
priority: P2
effort: S
status: done
classes: defect, infra
feature: parallel-sessions
milestone: v0.2.8
touches: .claude/hooks/docket-branch-guard.sh, .claude/settings.json, subprojects/docket/src/docket/cli.py, subprojects/docket/tests/test_cli.py, tests/unit/test_docket_branch_guard.py, subprojects/docket/README.md
added: 2026-09-01
closed: 2026-09-01
pr: 127
verify: uv run pytest -k branch_guard
---

**Problem.** `PL-1CYR` moved the branch-vs-`main` decision out of the
session-start hook and into `bin/docket branch`, so the question can be asked
at any moment. Nothing asks it. A command that exists but is never run closes
nothing: the gap `PL-1CYR` described - a session opened to discuss work, whose
base moves under it before the discussion becomes implementation - is now
*closable* rather than closed.

**Why it matters.** It is the same rework cycle `PL-1CYR` was written to
prevent, and it is paid in the sessions the project owner uses to think, which
are the ones that must stay cheap. Leaving it to a session to remember is the
weakest of the four dispositions in `CLAUDE.md`'s routing rule, and the moment
the check is wanted is one a hook can name exactly: the first edit.

**Where.** A `PreToolUse` hook on `Edit|Write|MultiEdit|NotebookEdit`, run once
per session, calling `bin/docket branch` and saying nothing when the branch is
current.

**Done when.** A session whose base moved while it was talking is told so
before its first edit, whether or not it thought to ask; a session on a current
branch sees nothing; and the check runs once per session rather than once per
edit.

**Triaged 2026-09-01**, at the project owner's direction, who chose this over
the cheaper alternative of naming the command in the session digest. P2,
`defect`/`infra`, `parallel-sessions` - the feature `PL-1CYR` completed, which
this reopens by one item because the completion was of the mechanism rather
than of the problem.

Two things the hook must get right, and both are why this is not a one-liner.
**Plain stdout from a `PreToolUse` hook reaches the debug log and nothing
else**, so a hook that echoes the line would look correct in a terminal and be
invisible to the session - the output has to be the documented JSON form
carrying `additionalContext`. And it must **not** send `permissionDecision:
allow`, which would auto-approve the edit it is attached to: the hook is there
to say something, never to grant something.

The `verify:` command keys on `branch_guard`, which selects nothing today.

**Done 2026-09-01.** `.claude/hooks/docket-branch-guard.sh` on
`Edit|Write|MultiEdit|NotebookEdit`, running `bin/docket branch --brief
--if-stale` once per session behind a marker keyed on the session id the hook
is handed. `--if-stale` is the new flag: say nothing unless the branch is
behind, which is what makes a hook that speaks unasked bearable.

Both hazards named above were confirmed against the current hooks
documentation before the hook was written, rather than after. Plain stdout on
exit 0 reaches the debug log only, so the line travels as `additionalContext`
inside `hookSpecificOutput`; `python3 -m json` does the escaping, because the
text carries backticks, quotes and newlines. `permissionDecision` is absent, so
the hook cannot auto-approve the edit it is attached to, and a test asserts
that key stays absent - it is one key away from being a permission grant that
nobody asked for.

Five tests in `tests/unit/test_docket_branch_guard.py` cover it against a real
`file://` remote: the JSON reaching the session, the absent permission key, the
once-per-session marker (including that a second session gets its own answer),
silence on a current branch, and exit 0 with nothing printed when the hook
cannot run at all.

**Demonstrated on itself while it was being built.** `bin/docket branch` in this
session reported the branch 1 behind `origin/main` and named `PL-1CYR` as what
had landed - which was true: pull request 125 had merged mid-session, and the
session-start digest still said the branch was current. That is exactly the
staleness `PL-1CYR` described and this item closes.
