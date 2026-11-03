---
id: PL-H8NX
title: thread_hooks.py re-runs the repository's SessionStart commands when the hooks block changed between two starts in one container, while Claude Code already runs the copies it installed, so the digest, fetch and effort-trial write run twice
priority: P3
effort: S
status: ready
classes: defect
feature: guard-review-2026-11
touches: .claude/hooks/thread_hooks.py, tests/unit/test_thread_hooks.py
deferred-from: v0.7.0 - captured after the freeze; a guard-hook defect in the workflow lane, not safety or science, and no learner sees it
added: 2026-11-03
payoff: a thread's session start runs the digest and the fetch once, not twice, after main changes the hooks
verify: grep -q 'def test_a_changed_hooks_block_does_not_rerun_start_commands' tests/unit/test_thread_hooks.py
---

**Problem.** thread_hooks.py re-runs the repository's SessionStart commands when the hooks block changed between two starts in one container, while Claude Code already runs the copies it installed, so the digest, fetch and effort-trial write run twice

**Why it matters.** `thread_hooks.main` runs the repository's `SessionStart`
commands whenever it rewrites the user settings. After the first start, the
copies it installed already run on their own, so any later start that finds
the hooks block changed (a pull of `main` between two sessions in one
container) runs the digest, the fetch and the effort-trial write twice.

**Done when.** The repository's `SessionStart` commands are run only when the
user settings held no copy of them before the write, and a test with a changed
hooks block over an existing copy finds them not run.

**Generator check.** A one-off in the bridge's first-run test.
