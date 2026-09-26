---
id: PL-20DL
title: claim reads its own published claim as unpushed where the branch's tip on the remote is a commit this clone has not fetched, so after someone else pushes to the branch, claim --no-fetch exits 4 saying only this checkout can see a claim every clone can
priority: P2
effort: S
status: done
classes: defect
feature: claim-integrity
touches: subprojects/docket/src/docket/claiming.py, subprojects/docket/tests/test_claiming.py, .claude/skills/docket/modes/start.md
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by its own thread's triage, 2026-09-26
added: 2026-09-26
closed: 2026-09-26
payoff: a session whose branch someone else pushed to is told its claim's visibility is unknown and to run claim again, not that the claim is local, and a published claim is never withdrawn for a later one
verify: grep -q 'def test_a_claim_under_a_commit_this_clone_has_not_fetched_is_not_reported_local' subprojects/docket/tests/test_claiming.py && grep -q 'def test_a_published_claim_under_a_commit_this_clone_has_not_fetched_is_not_withdrawn' subprojects/docket/tests/test_claiming.py
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

**Re-confirmed 2026-09-26 against `f760d01f`**, `main` with `PL-21KN`'s fix,
by three real-git tests added to `subprojects/docket/tests/test_claiming.py`,
each failing there for the reason below. The shape above still exits 4 saying
only this checkout can see the claim, and names `claim --push`. The half
inferred above is reproduced too. With a later claim on another branch, written
by hand since `claim` would refuse it, `claim --no-fetch` exits 3 and commits
a yield withdrawing this branch's claim, which every clone reads as holding
first. `_published` has a third caller, `yield` run again, which does not
fetch at all. After another writer's push it says the yield is not pushed and
only this checkout can see it, and names a `git push` that git would refuse as
a non-fast-forward.

**Why it matters.** `claim` is how a session tells every other session it has
an item, and its exit status is read as that evidence. After *Update branch* or
a second session's push, the holder is told its claim is invisible and sent to
a push git refuses. The withdrawal case is worse. The session is told another
branch holds its item, and the yield it was handed ends its own published
claim with its next push. That hands the item to a claim made later.

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
lacks, `claim` does not report a published claim as local-only, and does not
withdraw it. `yield` run again does not report its published yield as
local-only either. Real-git tests in
`subprojects/docket/tests/test_claiming.py` hold the three shapes above.

**Done, 2026-09-26.** `_published` answers `None` where `merge-base
--is-ancestor` exits anything but 0 or 1, and each of its three callers says
so instead of reading "no". `claim` on an item this branch already holds exits
4, says whether the remote's copy carries the claim is not known, names that
copy's tip, pushes nothing, and asks for `bin/docket claim <id>` again, which
fetches first. `_displaced` withdraws nothing on an unknown, as it already
waited where the remote could not be asked. `yield` run again says the same and
names `git fetch origin`, since it does not fetch itself.
`.claude/skills/docket/modes/start.md` now lists this third meaning of exit 4.

`PL-21KN`'s approach fits in its first half, and not in its second. The
unknown is the same exit 128, and it is said the same way. But `arm` names a
`git pull` because its question is whether `HEAD` is what the pull request
lands, which needs the commits merged in. `claim` and `yield` only ask whether
the remote's copy carries one commit, and the tip's objects answer that. A
fetch brings them without touching the working tree, and `claim` fetches
already. The tracking-ref fallback `_on_copy` takes was not taken here. For
this branch's own copy it would answer `CLAIMED` from the clone's copy of the
remote, which is `PL-MT3R`'s misread again. `_on_copy` takes it only because
its caller must err one way, and toward "the rival published" is the safe way.
