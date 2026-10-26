---
id: PL-TNY6
title: A Projects thread's copied hooks find their scripts through CLAUDE_PROJECT_DIR at run time, so when the session's working directory moves away from the checkout every hook fails and post_message is refused
priority: P2
effort: S
status: ready
classes: defect, infra
feature: projects-trial
touches: .claude/hooks/thread_hooks.py, tests/unit/test_thread_hooks.py
deferred-from: v0.7.0 - captured after the cut and not classed safety or science; fixed on its own branch the day it was filed
added: 2026-10-26
payoff: a Projects thread's copied hooks find the checkout even after the session's working directory moves, so no guard blocks the tool it guards
verify: grep -qF 'def test_a_copied_hook_finds_the_checkout_after_the_working_directory_moves' tests/unit/test_thread_hooks.py
---

**Problem.** `.claude/hooks/thread_hooks.py` (`PL-X6VN`) copies the
repository's `hooks` block into `~/.claude/settings.json` unchanged. Each
copied command finds its script as `"$CLAUDE_PROJECT_DIR/.claude/hooks/..."`,
and `hook_input.project_root()` reads the same variable. Claude Code sets
`CLAUDE_PROJECT_DIR` from the session's primary working directory. On
2026-10-26 at about 03:23Z, the harness moved one thread's working directory
from `/home/user/open-anesthesia-sim` to `/home/user`. Every copied hook then
looked for `/home/user/.claude/hooks/...`, which does not exist. The
owner-ask guard on `post_message` failed with "can't open file", so the
thread could not reply to the owner at all.

**Why it matters.** A guard that cannot find its script does not degrade
quietly. It blocks the tool it guards, and here that tool is the only way a
thread reaches the owner. The same move would also point every guard that
runs at the wrong directory.

**Done when.** The copied hooks find the checkout from where
`thread_hooks.py` itself sits, not from `CLAUDE_PROJECT_DIR` at run time. A
test in `tests/unit/test_thread_hooks.py` runs a copied command with
`CLAUDE_PROJECT_DIR` set to another directory and shows that it still acts on
the checkout.

**Found by.** The "Fix recurring and P1 items" thread, when its merge reply
for #1858 was refused, 2026-10-26. The coordinator asked for the fix.

**Generator check.** Not a generator. It is one defect in one mechanism,
`PL-X6VN`'s copier, and no other item names the same cause.
