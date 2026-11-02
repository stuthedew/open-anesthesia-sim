---
id: PL-L08H
title: The direct-merge guard refuses a session's merge in any repository whose base branch does not bind admins, though it exists to guard only this repository's main; it refused stuthedew/open-anesthesia-sim-references PR 1, which has no branch protection and no CI, so the merge fell to the owner for nothing
priority: P2
effort: S
status: ready
classes: defect
touches: .claude/hooks/direct-merge-guard.sh, tests/unit/test_direct_merge_guard.py
deferred-from: v0.7.0 - captured after the freeze (2026-11-02), a workflow defect and not safety or science
added: 2026-11-02
payoff: a session merges a pull request in the references corpus itself, while the guard still holds this repository's main to its required checks
verify: grep -q 'def test_a_merge_in_another_repository_is_let_through_unread' tests/unit/test_direct_merge_guard.py && grep -q 'def test_a_merge_in_this_repository_is_judged_by_its_own_origin' tests/unit/test_direct_merge_guard.py
---

**Problem.** The direct-merge guard refuses a session's merge in any repository whose base branch does not bind admins, though it exists to guard only this repository's main; it refused stuthedew/open-anesthesia-sim-references PR 1, which has no branch protection and no CI, so the merge fell to the owner for nothing

**Found 2026-11-02.** A session editing the references corpus for `PL-VW91`
tried to squash-merge `stuthedew/open-anesthesia-sim-references` PR 1 and the
hook refused it. The owner merged it by hand at 15:29 UTC and asked why a
session could not.

**Why it matters.** `.claude/hooks/direct-merge-guard.sh` exists so that a
session's direct merge cannot put a stale branch on this repository's `main`,
the merge skew `PL-6MW8` made `main` refuse. It lets a merge through only while
the base branch's `required_status_checks.enforcement_level` reads `everyone`.
It asks that of whatever repository the merge call names. The corpus repository
has no branch protection and no CI, so there was no check for the merge to skip
and no skew to prevent. The refusal guarded nothing and handed the owner a click.
The corpus is private as well, so the hook's tokenless read of it fails, and the
hook refuses on that ground too.

**Approach.** Judge only a merge into the repository the hook is checked into.
That repository is read from `tools/open_pull_requests.repo_slug`, the one
reading of which GitHub repository a checkout is (`PL-LGDV`), so no slug is
written into the hook. A merge naming another repository passes to the ordinary
permission flow, unread. Where the checkout's `origin` names no GitHub
repository, the hook cannot tell which merges are its own, so it judges every
merge as before. That is the safe direction.

**Generator check.** A one-off. The fact misread is which repository the guard
protects. The hook was written when this was the only repository a session
merged in, and no head's `misread:` states that fact.

**Done when.** A merge in another repository passes the hook unread, and a
merge in this repository is still refused while its `main` exempts admins, with
a test for each in `tests/unit/test_direct_merge_guard.py`.
