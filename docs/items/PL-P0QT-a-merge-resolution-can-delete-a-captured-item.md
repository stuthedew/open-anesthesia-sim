---
id: PL-P0QT
title: A merge resolution can delete a captured item with nothing recording that it did, and nothing checks for it
priority: P2
effort: S
status: done
classes: defect, infra
feature: parallel-sessions
touches: subprojects/docket/, tools/
added: 2026-09-02
closed: 2026-09-02
verify: uv run pytest subprojects/docket/tests/test_vcs.py subprojects/docket/tests/test_cli.py && grep -q 'def test_lost_finds_the_item_a_merge_resolution_removed' subprojects/docket/tests/test_cli.py
---

**Problem.** `PL-Q8QX` was captured on the v0.3.0 release branch in `ce090b4`
and is present in that commit's tree and in `d7d5272`. It is absent from
`24cbed1`, the merge that brought `main` into that branch, and therefore
absent from `main`. No commit in the branch's history deletes it — the merge's
own tree does, as part of a conflict resolution. `git log --diff-filter=D`
over the path returns nothing, which is why the loss left no trace a reader
would find.

**Observed** 2026-09-02, while re-scoring `PL-SZ56`'s readout 4 for the v0.3.0
close-out. `bin/docket stranded` still listed the item, but only because this
container held a stale `origin/` ref for a branch already deleted from the
remote. That ref was the only surviving copy.

**Why it matters.** `CLAUDE.md`'s capture rule is the project's guarantee that
a finding raised in a session is not lost, and the whole queue rests on it. A
merge that can silently drop an item file breaks that guarantee in the one
place nobody looks — a conflict resolution is reviewed as a merge, not as a
set of deletions, and a squash merge then collapses the evidence.

This instance was harmless, and only by luck: `PL-Q8QX` was a third filing of
the defect `PL-2XTF` carries. The second, `PL-9GCV`, was dropped in `#224` as
a duplicate with `reason:` recorded in its front matter and its file still in
the store. That is the contrast that matters — a duplicate closed by a
decision stays legible afterwards, and one removed by a merge resolution does
not. The next item lost this way may be the only filing of its finding.

**Where, and what would catch it.** The decidable half is small: a check that
compares the set of item ids on the default branch against the set on each
merged branch tip, and reports any id that existed on a merged branch and is
absent from `main` without a `dropped` record. `bin/docket stranded` already
walks branch refs and already knows which items exist only on a branch; this
is the same walk asking the opposite question, and it is the one `stranded`
cannot answer today because a merged, deleted branch stops being a ref at all.

Two narrower guards are worth considering alongside it and are cheaper: refuse
a merge whose tree deletes a `docs/items/*.md` file that no commit in the
merge's history deletes, and have `docket check` report an id referenced by a
release note or another item's brief that resolves to no file.

**Not the same as `PL-64LS` or `PL-2XTF`.** `PL-64LS` detects an item stranded
on an *unmerged* branch, which is the live case `stranded` handles. This is
the opposite: a branch that merged, whose item did not. `PL-2XTF` is about
recovering a pull request number from a squash subject, which is how
`PL-Q8QX`'s own content came to be filed three times.

**On `PL-Q8QX` itself.** It is not restored here. Its content is a duplicate of
`PL-2XTF`, which carries the same `#220` incident with a fuller brief, and
re-filing it would repeat the duplication `#224` cleared. Its finding is
described in the v0.3.0 close-out's readout 4 discussion, and its file is
recoverable with `git show d7d5272:docs/items/PL-Q8QX-docket-check-cannot-recover-a-pull-request.md`
for as long as a checkout holds that ref — which is the fragility this item is
about, not a substitute for fixing it.

**Done when.** A check reports an item id that existed on a branch now merged
into the default branch and is absent from it with no `dropped` record, with a
test covering the merge-deletes-a-file case, and `PL-Q8QX` is recorded as
superseded by `PL-2XTF` rather than silently absent.

**How it was built, and where it differs from the plan above.** The check is
`vcs.lost`, wired into `docket check` as an *error*. It compares the item ids
in a ref's tree against the ids in every blob path reachable from that ref, so
the deletion a merge performs in its own tree is visible even though no
commit's diff shows it. Comparison is by id rather than path, so a renamed
item file is not a loss.

The plan above asked for a check "run on `main`", comparing the default branch
against merged branch tips. **That cannot work, and measuring it is what
changed the design.** After a squash merge the branch's commits are ancestors
of nothing, so its objects stop being reachable: `PL-Q8QX`'s own blob is
reachable from no commit `main` holds, and a check run there reports the store
clean and is wrong to. Since a false clean bill of health on the capture rule
is worse than no check at all, the walk asks the *branch* instead, in CI, on
the pull request, before the squash collapses the history. It still catches an
ordinary merge on `main`; nothing run there can catch a squashed one.

Two facts were measured rather than assumed, and both are asserted in the
tests so they cannot rot: `git log --diff-filter=D` really does miss the
deletion, and `rev-list --objects` really does list newest-blob-first, which
is what lets the report hand back the item as it last stood rather than as it
was captured. `PL-Q8QX` is restored as a `dropped` record naming `PL-2XTF`.
