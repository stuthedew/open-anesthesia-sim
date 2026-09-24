---
id: PL-PXZ3
title: left_behind_check reports a commit whose identical patch already landed through another pull request: its first finding, 52c6d698 on claude/recurrence-signal-feature-3hnynt, matches 98de88c8 in #794 by git patch-id, so the reader had to prove the branch stale by hand
priority: P3
effort: M
status: done
classes: defect
feature: landed-elsewhere
milestone: v0.5.9
touches: tools/left_behind_check.py, tests/unit/test_left_behind_check.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the second 2026-09-23 triage pass
added: 2026-09-23
closed: 2026-09-23
pr: 975
payoff: the digest's left-behind line stops naming commits that already merged through another pull request, so a finding there is one worth acting on
verify: grep -q 'def test_a_commit_whose_patch_landed_through_another_pull_request_is_not_left_behind' tests/unit/test_left_behind_check.py
---

**Problem.** left_behind_check reports a commit whose identical patch already landed through another pull request: its first finding, 52c6d698 on claude/recurrence-signal-feature-3hnynt, matches 98de88c8 in #794 by git patch-id, so the reader had to prove the branch stale by hand

**Found 2026-09-23** on the session-start digest's first `left-behind:` line.
`git show 52c6d698 | git patch-id --stable` equals the patch-id of `98de88c8`
in `refs/pull/794/head`, and #794 squash-merged as `9fe0ee33` (PL-DGP0,
`pr: 794`). The check's own output already says it cannot tell this case
("if the change landed through another pull request, the branch is stale"),
so this is a precision gap in an existing check rather than a wrong answer:
it could compare a left-behind commit's patch-id against other pull requests'
heads before reporting it. Held as a capture under the `PL-6Q9L` pause unless
it is read as a defect in what exists.

**Reproduced at triage, 2026-09-23, only as far as the code.**
`claude/recurrence-signal-feature-3hnynt` has been deleted and
`tools/left_behind_check.py` reports no finding today. Its docstring states the
case as a known disagreement - a commit whose change "landed through *another*
pull request shows up here" while "`orphaned` stays silent, because the content
is on the base" - and nothing in the tool computes a patch-id. `PL-GHHW` shows
the docstring's second clause failing: `orphaned` also reports such a commit
once the base's copy of the file has moved on.

**Why it matters.** Every such finding sends the reader to prove staleness by
hand, by `patch-id` against pull-request heads, on the digest's `left-behind:`
line that every session start reads; and the drive-to-green rules make porting a
fix that is also landing elsewhere routine, so the findings recur.

**Done when.** A left-behind commit whose `git patch-id --stable` matches a
commit on another pull request's head is reported as having landed through that
pull request, naming its number, instead of as work left behind, pinned by a
test with a fake runner.

**Generator check.** Grouped with `PL-GHHW` under `landed-elsewhere`, as that
item's check says. The `PL-6Q9L` pause cited above has ended - no open item
carries `generator: live` - and this is in any case a precision fix to an
existing check.

**Closed 2026-09-23 with `PL-GHHW`**, the generator head that explains it, as
the project owner asked (project owner, 2026-09-23). `left_behind_check.examine`
now asks `vcs.change_landed` of each commit past the merged head, and a commit
whose change the default branch took through another pull request is
reported as having landed there, naming its number, rather than as work left
behind: the branch reads as clear in the digest, and `--all` lists the commit
beside `landed through #N`. Two departures from the Done-when above, both
deliberate. The number comes from the landing commit's squash subject rather
than from a patch-id match against another pull request's head, since that
match needs `refs/pull/*` in the checkout and fails whenever the other pull
request's squash carries more than the port. And the tests are real
repositories (`test_a_commit_whose_patch_landed_through_another_pull_request_is_not_left_behind`
and the mixed case beside it), not a fake runner, because the question is what
git's merge makes of two histories.
