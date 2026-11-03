---
id: PL-KJN6
title: direct-merge-guard.sh and thread_hooks.COMMAND_TIMEOUT_S say Claude Code's default hook timeout is 60 s, which the hooks documentation now gives as 600 s, and docs/apparatus.md names neither thread_hooks.py nor hook_input.py among the hook files nothing wires
priority: P3
effort: S
status: ready
classes: docs, defect
feature: guard-review-2026-11
touches: .claude/hooks/thread_hooks.py, .claude/hooks/direct-merge-guard.sh, docs/apparatus.md
deferred-from: v0.7.0 - captured after the freeze; a guard-hook defect in the workflow lane, not safety or science, and no learner sees it
added: 2026-11-03
payoff: the bridge gives a repository SessionStart command the time Claude Code would, and the hook map names every file nothing wires
verify: grep -q 'COMMAND_TIMEOUT_S = 600' .claude/hooks/thread_hooks.py
---

**Problem.** direct-merge-guard.sh and thread_hooks.COMMAND_TIMEOUT_S say Claude Code's default hook timeout is 60 s, which the hooks documentation now gives as 600 s, and docs/apparatus.md names neither thread_hooks.py nor hook_input.py among the hook files nothing wires

**Read 2026-11-03.** https://code.claude.com/docs/en/hooks gives the defaults
as "600 for `command`, `http`, and `mcp_tool`; 30 for `prompt`; 60 for
`agent`".

**Why it matters.** `COMMAND_TIMEOUT_S` in `thread_hooks.py` and a comment in
`direct-merge-guard.sh` state Claude Code's default command-hook timeout as 60
s. The documentation gives 600 s, so the bridge kills a repository
`SessionStart` command sooner than Claude Code would, and the comment
misleads the next reader. `docs/apparatus.md` § "Wired hooks" says
`shell_split.py` is the one file nothing wires, which is no longer true.

**Done when.** Both statements match the hooks documentation as read on the
day of the fix, with the date, and `docs/apparatus.md` names
`thread_hooks.py` and `hook_input.py` among the files nothing wires.

**Generator check.** A one-off: an external default restated and gone stale.
