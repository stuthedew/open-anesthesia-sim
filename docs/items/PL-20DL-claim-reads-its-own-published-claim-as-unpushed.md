---
id: PL-20DL
title: claim reads its own published claim as unpushed where the branch's tip on the remote is a commit this clone has not fetched, so after someone else pushes to the branch, claim --no-fetch exits 4 saying only this checkout can see a claim every clone can
status: untriaged
touches: subprojects/docket/src/docket/claiming.py, subprojects/docket/tests/test_claiming.py
added: 2026-09-26
---

**Problem.** claim reads its own published claim as unpushed where the branch's tip on the remote is a commit this clone has not fetched, so after someone else pushes to the branch, claim --no-fetch exits 4 saying only this checkout can see a claim every clone can

**What was seen.** Reproduced 2026-09-26 with a scratch real-git test built
on `subprojects/docket/tests/test_claiming.py`'s fixtures, on `12f30452` with
`PL-C3MN`'s change. A clone claims `PL-B1B1` and pushes the claim. A second
clone pushes one more commit onto the same branch, the shape GitHub's *Update
branch* leaves. The first clone then runs `bin/docket claim PL-B1B1
--no-fetch`, which exits 4 (`LOCAL_ONLY`) and prints:

```
PL-B1B1: claude/work-b7xq2n already holds it first; nothing written for it
PL-B1B1: claim 17aa903b0b05 on claude/work-b7xq2n, and not pushed, so only this checkout can see it: the branch is on the remote as origin/claude/work-b7xq2n, ...
```

The claim was on the remote, under the other clone's commit, and every clone
could fetch it. The remedy the message names, `claim --push`, would then be
refused as a non-fast-forward.

**Where it comes from.** `claiming._published` asks `git merge-base
--is-ancestor <claim> <tip>` with the tip `_on_remote` read from the
command's listing, and takes any exit but 0 as "does not carry it". Where the
tip is a commit this clone has not fetched, git exits 128 ("Not a valid
commit name"): it cannot answer, which is not the same as the claim being
absent. On the path for an item this branch already holds, the claim is then
treated as unpushed and handed to `_publish`, which holds it back from a
branch the remote has, with the message above. `_displaced` asks the same
question, so it could take this branch's published claim for unpublished and
withdraw it in favour of a later rival. That half is inferred, not
reproduced: `claim` refuses such a rival wherever it can see this branch's
claim. With the default fetch, the window is a push that lands between
`claim`'s fetch and its listing.

**A direction, not a decision.** Have `_published` say "unknown" where git
cannot answer (an exit other than 0 or 1), and have each caller say so rather
than read "no". The already-held path would then say the remote's branch has
commits this clone lacks, and to fetch or bring them in and run again.
`_displaced` would withdraw nothing on an unknown, as it already waits where
the remote could not be asked. `_on_copy` has drawn the same line since
`PL-C3MN`, falling back to the tracking ref for a rival's branch, so one
helper answering "does this tip carry that commit, or can git not say" could
serve both.

**Not a recurrence of `PL-C3MN`.** `docket new` matched this capture to
`PL-C3MN` on shared paths and wording. It is a different reader of the same
fact: `_published`, reading this branch's own copy, not `_on_copy`'s rival
read firing again. So the match is withdrawn.

**Generator check.** An instance of `PL-MT3R`'s fact, "The remote's current
refs and tags, and whether the clone's local copies still match them": here
the clone's objects do not reach the tip the listing names. It is the first
since that head closed on 2026-09-26. Its trigger, another writer pushing to
the branch, is the one `PL-21KN` records for `arm`.

**Done when.** Where the listing names a tip for this branch that the clone
lacks, `claim` does not report a published claim as local-only. A real-git
test in `subprojects/docket/tests/test_claiming.py` holds the shape above.
