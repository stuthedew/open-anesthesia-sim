---
id: PL-SRQB
title: docket-branch-guard.sh spends its once-per-session claim question on a detached HEAD or main, where branch_id_check --hint is silent, so the first edit on a new work branch is never asked
priority: P2
effort: S
status: done
classes: defect
feature: guard-review-2026-11
milestone: v0.6.15
touches: tools/branch_id_check.py, tests/unit/test_branch_id_check.py
deferred-from: v0.7.0 - captured after the freeze; a guard-hook defect in the workflow lane, not safety or science, and no learner sees it
added: 2026-11-03
closed: 2026-11-03
pr: 1989
payoff: a session that starts on main is still told to claim an item at its first edit on the work branch it then creates
verify: grep -q 'def test_hint_on_a_detached_head_is_not_asked' tests/unit/test_branch_id_check.py
---

**Problem.** docket-branch-guard.sh spends its once-per-session claim question on a detached HEAD or main, where branch_id_check --hint is silent, so the first edit on a new work branch is never asked

**Why it matters.** The guard asks "this branch claims nothing" once per
session. On a detached HEAD or on `main`, `branch_id_check.py --hint` prints
nothing and exits 0, which the hook reads as asked, so the question is spent
before the session creates its work branch and the first edit there is never
asked.

**Done when.** `--hint` exits `NOT_ASKED` on a detached HEAD and on the default
branch, so the question waits for a work branch, and a test pins both.

**Generator check.** A one-off in one exit status.
