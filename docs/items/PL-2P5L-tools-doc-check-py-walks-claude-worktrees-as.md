---
id: PL-2P5L
title: tools/doc_check.py walks .claude/worktrees/ as repository source, because _walk skips only its own IGNORED_DIRS and never asks git what is ignored, so a broken quotation in a worktree-isolated agent's copy fails doc_check in the main checkout
priority: P3
effort: S
status: ready
classes: defect
feature: agent-worktrees
touches: tools/doc_check.py, tests/unit/test_doc_check.py
deferred-from: v0.6.0 - filed after the freeze by the 2026-09-24 triage pass, and not safety or science
added: 2026-09-24
payoff: doc_check stops failing a session's tree for errors in another agent's worktree
verify: grep -q 'def test_a_worktree_under_claude_worktrees_is_not_walked' tests/unit/test_doc_check.py
---

**Problem.** tools/doc_check.py walks .claude/worktrees/ as repository source, because _walk skips only its own IGNORED_DIRS and never asks git what is ignored, so a broken quotation in a worktree-isolated agent's copy fails doc_check in the main checkout

**Found 2026-09-24 at triage**, while reproducing `PL-M9QW` in a scratch clone.
A broken quotation that existed only in a worktree's copy under
`.claude/worktrees/` failed `tools/doc_check.py` in the main checkout. `_walk`
skips only its own `IGNORED_DIRS` and never asks git what is ignored, so the
ignore rule `PL-M9QW` adds does not reach it.

**Why it matters.** A session is told its own tree is broken because of
another agent's work in progress, which sends it to repair a file that is not
in its checkout.

**Done when.** `tools/doc_check.py` does not walk `.claude/worktrees/`, and a
test in `tests/unit/test_doc_check.py` pins it.

**Generator check.** A one-off. It shares its trigger with `PL-M9QW`, but not
its mechanism: this one is the tool's own directory list, and that one is the
ignore file.
