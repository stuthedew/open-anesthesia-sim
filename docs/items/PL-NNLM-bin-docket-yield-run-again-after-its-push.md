---
id: PL-NNLM
title: bin/docket yield run again after its push failed says the claim has already ended and pushes nothing, so the yield stays in this checkout while every other session still reads the item as held
status: untriaged
feature: claim-integrity
touches: subprojects/docket/src/docket/claiming.py, subprojects/docket/tests/test_claiming.py
added: 2026-09-25
---

**Problem.** bin/docket yield run again after its push failed says the claim has already ended and pushes nothing, so the yield stays in this checkout while every other session still reads the item as held

**Reproduced, 2026-09-25**, in `PL-WX87`'s session against a scratch bare
remote: a claim pushed, then the remote lacking the branch and refusing pushes
(`pre-receive` exiting 1). `bin/docket yield PL-B1B1` wrote the yield, failed
to push, and exited 4 with "it is local: no other session can see it". With
the hook removed, `bin/docket yield PL-B1B1` exited 0 printing
"claude/work-b7xq2n's claim on it has already ended; nothing written", and the
remote still had no copy of the branch.

**Why.** `claiming.yield_claims` decides what to write from `holdings`, which
reads the local branch, where the yield commit already stands, so the hold
reads as released and the call returns before `_publish`. `claim` has the
retry `yield` lacks: an item the branch already holds whose claim commit the
remote's tip does not carry goes to `_publish` again, by `_published`.

**Why it matters.** Until the lease runs out, seven days past the branch's
last commit, every other session reads the item as held by a session that has
stopped, and the rerun's exit 0 is what the yielding session reports. The same
shape as `PL-1X56`, whose `claim` path exited 0 for a claim no other session
could see until #1026; the recurrence line there is this filing. That fix
reaches `_publish` alone, which the rerun returns before.

**Already done.** `PL-WX87`'s branch stopped the failed-push message telling a
yield to "run this again", since that pushes nothing; it names the push
command alone. What is left is the retry.

**Done when.** `bin/docket yield` run again on a branch whose yield the remote
does not carry pushes it, as `claim`'s retry does, or exits non-zero saying
the yield is local; a real-git test in `subprojects/docket/tests/test_claiming.py`
holds the rerun.
