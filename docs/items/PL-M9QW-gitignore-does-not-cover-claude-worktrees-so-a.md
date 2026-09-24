---
id: PL-M9QW
title: .gitignore does not cover .claude/worktrees/, so a worktree-isolated workflow agent's live checkout shows as untracked and the stop hook asks the session to commit and push it
priority: P3
effort: S
status: ready
classes: defect
feature: agent-worktrees
touches: .gitignore
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-09-24 triage pass
added: 2026-09-24
payoff: the stop hook stops telling a session to commit and push another agent's live checkout
verify: grep -qF '/.claude/worktrees/' .gitignore
---

**Problem.** .gitignore does not cover .claude/worktrees/, so a worktree-isolated workflow agent's live checkout shows as untracked and the stop hook asks the session to commit and push it

**Premise re-checked at triage, 2026-09-24.** `git check-ignore -v
.claude/worktrees/x/y` exits 1. In a scratch clone, after `git worktree add
.claude/worktrees/agent-x`:

- The harness's stop hook listed `.claude/worktrees/agent-x/` as untracked and
  exited 2 with "There are untracked files in the repository. Please commit and
  push".
- With `/.claude/worktrees/` ignored, the hook exited 0 and `ruff check .`
  stopped linting the copy.

The hook reads `git ls-files --others --exclude-standard`, so the ignore rule
is the whole fix for it.

**Why it matters.** The hook tells the session to commit and push another
agent's live checkout, which is the one instruction here that must not be
followed.

**Done when.** `.gitignore` ignores `/.claude/worktrees/`. `PL-2P5L`, filed
alongside this, covers `tools/doc_check.py` walking that copy anyway.

**Generator check.** A one-off: the harness creates a directory that the
ignore file predates.
