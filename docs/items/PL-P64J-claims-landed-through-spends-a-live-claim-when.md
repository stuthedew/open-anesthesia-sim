---
id: PL-P64J
title: claims._landed_through spends a live claim when the branch, as of some commit after the claim, only restores files to content the default branch held before the fork, because it splits that commit against the base's ever-held blob set: a claimed branch retiring a feature by restoring files reads as merged, and its item as unheld
priority: P2
effort: S
status: done
classes: defect
feature: pre-fork-content
touches: subprojects/docket/src/docket/claims.py, subprojects/docket/tests/test_claims.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science
added: 2026-09-26
closed: 2026-09-27
pr: 1160
payoff: a claimed branch that restores files to earlier content keeps its claim, so the item still reads as held and no second session is offered it
verify: grep -q 'def test_a_claim_on_a_branch_restoring_pre_fork_content_stays_live' subprojects/docket/tests/test_claims.py
---

**Problem.** claims._landed_through spends a live claim when the branch, as of some commit after the claim, only restores files to content the default branch held before the fork, because it splits that commit against the base's ever-held blob set: a claimed branch retiring a feature by restoring files reads as merged, and its item as unheld

**Reasoned from the code on 2026-09-26, not yet run.** Found while fixing
`PL-RLTK`. A branch holding a claim and one commit that restores a file to a
blob `main` held before the fork: that commit's `added` blobs are all in
`refs.base_blobs`, so it passes the prefilter, and `_landing_split` against the
same ever-held set reads it as wholly landed, so the claim is spent. Before
`PL-RLTK`, `_unlanded_refs` excluded such a branch outright, so its claims were
never read; the visible answer, an unheld item, is the same either way.

It was left out of `PL-RLTK`'s fix on purpose. `_landed_through` splits an
older commit against the *tip's* fork, and below a grafted horizon it relies on
base commits reading as landed (`PL-W1LN`, `PL-N162`), so moving it to the
since-the-fork set needs each commit's own fork and a fresh look at that case.
`claims.py` is Stream B's file in `PL-NZC0`'s trial.

**Reproduced 2026-09-27**, by a scratch test built on `test_claims.py`'s
`_Repo` and not committed: `main` writes a file and then replaces it, a branch
forks after that, claims an item and commits the file back to its first
content. The claim reads `released`, `released_by='landed'`, both with the
restore as the branch's last commit and with new work after it; the control,
the same branch writing content `main` never held, keeps the claim live. The
one `_landing_split` call is on the restore commit, against the base's
ever-held set, and returns the file as wholly landed. It lives in
`_landed_through` in `subprojects/docket/src/docket/claims.py`, whose prefilter
and landing split both read `refs.base_blobs`, which `holdings` takes from
`vcs._base_blobs`.

**One correction to the title.** Since `PL-RLTK`, `vcs.landed_whole` says the
branch has *not* landed, so the branch no longer reads as merged; only its
claim does, and the claim is what leaves the item unheld.

**Why it matters.** A claim is the one record that tells every other session an
item is taken, and this one is spent while its branch is still open, so `next`,
`flight` and `show` offer the item as free and a second session can start it.
Restoring files to earlier content is what retiring or reverting a feature
does, so the case is ordinary work rather than an edge.

**Done when.** `_landed_through` spends a claim only for commits the base took
since the branch's fork, so a claimed branch whose commits restore files to
content the base held before the fork keeps its claim live, with or without
later work, and a test pins both beside the control where the branch writes new
content.

**Generator check.** A member of `PL-927J`, the head recorded at this triage
for the family fact `PL-R808`, `PL-BHVM` and `PL-GHHW` name: whether the base
already holds or has superseded a branch commit's change, by whatever route.

**Fixed 2026-09-27** through `PL-927J`. `_landed_through` asks
`vcs._Landings.taken_whole` of each descendant commit that wrote anything: the
commit's own fork, its net change since, against what the base wrote after
that fork. The ever-held prefilter went with the set. Pinned by
`test_a_claim_on_a_branch_restoring_pre_fork_content_stays_live`: the restore
keeps the claim live with and without later work, and a squash writing that
content after the fork spends it.
