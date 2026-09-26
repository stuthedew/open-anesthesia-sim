---
id: PL-C3MN
title: claim's withdrawal check reads a rival branch's tracking ref as the remote's copy of it, so a rival branch deleted on the remote but never pruned here still withdraws this branch's unpublished claim, in favour of a claim no fresh clone can see
priority: P2
effort: S
status: blocked
classes: defect
feature: claim-integrity
touches: subprojects/docket/src/docket/claiming.py, subprojects/docket/tests/test_claiming.py
blocked-by: PL-MT3R
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-09-26 triage pass
added: 2026-09-26
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
