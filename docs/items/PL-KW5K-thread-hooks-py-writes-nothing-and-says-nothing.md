---
id: PL-KW5K
title: thread_hooks.py writes nothing and says nothing when CLAUDE_CODE_ENTRYPOINT is anything but remote_projects, so a renamed entrypoint turns off every repository hook in Projects threads silently
priority: P2
effort: S
status: done
classes: defect
feature: guards-say-when-they-cannot-check
milestone: v0.6.15
touches: .claude/hooks/thread_hooks.py, .claude/hooks/hook_input.py, tests/unit/test_thread_hooks.py
deferred-from: v0.7.0 - captured after the freeze; a guard-hook defect in the workflow lane, not safety or science, and no learner sees it
added: 2026-11-03
closed: 2026-11-04
pr: 2005
payoff: a Projects thread whose hooks the bridge did not copy is told so at session start
verify: grep -q 'def test_an_unknown_entrypoint_says_the_hooks_were_not_copied' tests/unit/test_thread_hooks.py
---

**Problem.** thread_hooks.py writes nothing and says nothing when CLAUDE_CODE_ENTRYPOINT is anything but remote_projects, so a renamed entrypoint turns off every repository hook in Projects threads silently

**Read 2026-11-03.** `thread_hooks.main` returns an empty string when
`CLAUDE_CODE_ENTRYPOINT` is anything other than `remote_projects`. That is
right for an ordinary cloud session, which loads `.claude/settings.json`
itself. But if the harness renames the Projects entrypoint, a thread gets no
hooks and no line saying so.

**Why it matters.** Every guard in a Projects thread depends on this bridge.
Turned off by a rename, the thread works without any of them and believes it
has them.

**Done when.** A session start whose entrypoint is neither the Projects value
nor one this file knows to load the repository settings itself prints one line
naming the entrypoint and saying the repository's hooks were not copied, and a
test with an unknown entrypoint finds that line.

**Generator check.** A member of `PL-9KSJ`: the bridge switches every guard
off and says nothing.
