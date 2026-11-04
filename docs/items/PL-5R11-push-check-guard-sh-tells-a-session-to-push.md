---
id: PL-5R11
title: push-check-guard.sh tells a session to push work in progress with git push --no-verify, which also skips the pre-push hook's refusal of branch deletions and its email screen of the new commits
priority: P2
effort: S
status: ready
classes: defect
feature: guards-keyed-on-the-action
touches: .claude/hooks/push_check_guard.py, .claude/hooks/git/pre-push, tests/unit/test_push_check_guard.py, tests/unit/test_git_hooks.py
deferred-from: v0.7.0 - captured after the freeze; a workflow-lane guard defect, not safety or science, and no learner sees it
added: 2026-11-03
payoff: a work-in-progress push that skips the checks still has its commits screened for an email address and cannot delete a remote branch
verify: grep -q 'def test_a_work_in_progress_push_still_screens_for_an_address' tests/unit/test_git_hooks.py
---

**Problem.** push-check-guard.sh tells a session to push work in progress with git push --no-verify, which also skips the pre-push hook's refusal of branch deletions and its email screen of the new commits

**Found 2026-11-03, building `PL-1ZZ0`.** `push-check-guard.sh` refuses a push
until the checks pass, and its message says a work-in-progress push to a branch
with no pull request may go out with `git push --no-verify`. That flag skips
every `pre-push` hook. Since `PL-1ZZ0`, `.claude/hooks/git/pre-push` also
refuses a push that deletes a remote branch and screens the pushed commits for
an email address. So the one push the guard sends unchecked is also the one
push nothing screens for an address, and a commit is public once GitHub has
it.

<!-- absent: push-check-guard.sh -->

**Why it matters.** An address in a work-in-progress commit is as public as
one in a pull request. The exemption was written when the only `pre-push`
work was the checks, which a work-in-progress push may skip.

**Done when.** A work-in-progress push that skips the checks still runs the
deletion refusal and the email screen, for example by the guard or the hook
reading an environment variable instead of the session passing
`--no-verify`, and a test pushes a commit holding an address that way and
finds it refused.

**Generator check.** A member of `PL-1ZZ0`'s cause (a guard keyed on the
request's surface, here the `--no-verify` flag, instead of the action), which
`PL-1ZZ0` recorded spent once its fix merged. One more instance does not make
it live again, so this is fixed at its own rank.

**Sequencing.** `PL-S3TF` (#1990) moves push-check-guard.sh's Python into
`push_check_guard.py`. Build this after that merges, in the module, so the two
branches do not edit the same embedded Python.

