---
id: PL-C3MN
title: claim's withdrawal check reads a rival branch's tracking ref as the remote's copy of it, so a rival branch deleted on the remote but never pruned here still withdraws this branch's unpublished claim, in favour of a claim no fresh clone can see
status: untriaged
feature: claim-integrity
touches: subprojects/docket/src/docket/claiming.py, subprojects/docket/tests/test_claiming.py
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

**Done when.** A rival claim whose branch the remote no longer has does not
withdraw this branch's claim, or the withdrawal says the rival's copy was read
from a fetch that may be stale; a real-git test in
`subprojects/docket/tests/test_claiming.py` deletes the rival's branch on the
remote and holds the answer.
