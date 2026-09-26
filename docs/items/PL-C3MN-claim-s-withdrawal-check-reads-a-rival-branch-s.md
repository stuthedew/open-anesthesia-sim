---
id: PL-C3MN
title: claim's withdrawal check reads a rival branch's tracking ref as the remote's copy of it, so a rival branch deleted on the remote but never pruned here still withdraws this branch's unpublished claim, in favour of a claim no fresh clone can see
priority: P2
effort: S
status: done
classes: defect
feature: claim-integrity
touches: subprojects/docket/src/docket/claiming.py, subprojects/docket/tests/test_claiming.py
blocked-by: PL-MT3R
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-09-26 triage pass
added: 2026-09-26
closed: 2026-09-26
pr: 1119
payoff: a claim is never withdrawn in favour of a rival branch GitHub has deleted, so no item is left held by nobody
verify: grep -q 'def test_a_rival_whose_branch_the_remote_deleted_does_not_withdraw_the_claim' subprojects/docket/tests/test_claiming.py
recurrences: 2026-09-26 PL-20DL withdrawn 2026-09-26 PL-20DL
---

**Problem.** claim's withdrawal check reads a rival branch's tracking ref as the remote's copy of it, so a rival branch deleted on the remote but never pruned here still withdraws this branch's unpublished claim, in favour of a claim no fresh clone can see

**Found by reading, not reproduced**, while merging `PL-ZLJ9` (#1028) into
`PL-WX87`'s branch (#1024), 2026-09-26. `claiming._displaced` asks
`_on_copy(root, name, rival.commit)` whether a rival's claim is published, and
`_on_copy` reads `refs/remotes/origin/<rival>`, the ref as of the last fetch.
`claim`'s fetch never prunes (`vcs.fetch_remote`, deliberately), and
`vcs._unlanded_refs(include_remote=True)` reads every ref under
`refs/remotes`, so a rival branch deleted on the remote inside its seven-day
lease still reads as a live, published claim here. A claim of this branch's
that orders first and was never pushed is then withdrawn in its favour: exit 3
for an item asked for, while a fresh clone sees no rival at all, so the item
can end up held by nobody.

**Why it is this shape.** It is `PL-WX87`'s misreading - a clone's tracking
ref taken for the remote's copy - in the rival half of the check. `PL-WX87`
fixed it for this branch's own copy only, with one `git ls-remote` per run;
asking for every rival branch costs a round trip per branch unless one
listing of the remote's heads answers them all.

**Premise confirmed by reading, 2026-09-26, against `78b1a02b`.** One grep of
`claiming.py` and `vcs.py` showed `_on_copy` still building
`refs/remotes/{REMOTE}/{name}`. It also showed both of `claim`'s fetches as
`git fetch --quiet origin` with no `--prune`, and `vcs.fetch_remote`'s
docstring still keeping it "deliberately not `--prune`". Not yet reproduced
against a remote.

**Why it matters.** The withdrawal exists so that a claim already published
keeps its item (`PL-ZLJ9`). Reading a deleted rival as published inverts that,
in this checkout alone. This branch's claim is withdrawn and `claim` exits 3,
while a fresh clone sees no rival, so every other session reads the item as
held by nobody. The claim record exists to prevent exactly that (`PL-MB2W`).
The window lasts as long as a clone that fetched the rival before its deletion,
which is a session's container, hours. Nothing in the exit-3 message says the
rival's copy came from a fetch rather than from the remote.

**Done when.** A rival claim whose branch the remote no longer has does not
withdraw this branch's claim, or the withdrawal says the rival's copy was read
from a fetch that may be stale; a real-git test in
`subprojects/docket/tests/test_claiming.py` deletes the rival's branch on the
remote and holds the answer.

**Generator check.** An instance of `PL-4Q9B`'s fact, "The remote's current
refs and tags, and whether the clone's local copies still match them", and the
third since that head closed on 2026-09-19, after `PL-WX87` and `PL-KX73`. It
belongs to `PL-MT3R`, the head recording that the fix did not hold.

**Blocked, triage 2026-09-26, on `PL-MT3R`'s decision.** That head recommends
one `ls-remote --heads` listing per command for every reader of the remote's
copy, which is this item's fix. A fix made here alone would be one more
per-reader fix.

**Done, 2026-09-26 (#1119).** #1116 had already closed the case this brief
describes: `holdings` drops a tracking ref whose branch the listing lacks, so
a deleted rival read only through its tracking ref withdrew nothing on `main`.
It did not reach a local branch of the rival's name, which `holdings` still
reads as this checkout's own. There `_on_copy` found the unpruned tracking ref
carrying the claim and withdrew this branch's claim with exit 3, reproduced by
the `and-local-branch` case of the test the `verify:` names. `_on_copy` now
reads the rival's branch from the command's listing, as `PL-MT3R` decided. Where
the listing names a tip this clone has not fetched, git exits 128 rather than
answering, and the tracking ref is read as before, so a rival that pushed since
the fetch still withdraws the claim (`PL-ZLJ9`); a third test holds that.
`_published` has the same exit-128 misreading for this branch's own copy,
filed as `PL-20DL`.
