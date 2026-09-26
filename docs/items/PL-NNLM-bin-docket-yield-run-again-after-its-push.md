---
id: PL-NNLM
title: bin/docket yield run again after its push failed says the claim has already ended and pushes nothing, so the yield stays in this checkout while every other session still reads the item as held
priority: P2
effort: S
status: done
classes: defect
feature: claim-integrity
touches: subprojects/docket/src/docket/claiming.py, subprojects/docket/tests/test_claiming.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-09-26 triage pass
added: 2026-09-25
closed: 2026-09-26
payoff: a yield whose push failed reaches the remote when yield is run again, or says it did not, so no session reports a yield as done while every other session still reads the item as held
verify: grep -q 'def test_yield_run_again_after_its_push_failed' subprojects/docket/tests/test_claiming.py
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

**Premise confirmed by reading, 2026-09-26, against `78b1a02b`.** In
`claiming.yield_claims`, the "has already ended; nothing written" note and the
`if not writing:` return both still come before `_on_remote`, which is the only
place yield's path asks the remote. So the rerun decides from the local branch
alone. `_publish`'s failed-push comment still names this item.

**Generator check.** A re-entry of `PL-1X56` (done 2026-09-25): the same
mechanism at a sibling site, `yield` rather than `claim`, which that fix did
not cover because it reaches `_publish` alone. `PL-1X56` already lists this
filing under `recurrences:`. `PL-MT3R` counts the same local read among its
readers. The retry here can ask `_on_remote`, as `claim`'s does, without
waiting on that head's record.

**Closed 2026-09-26.** `claiming.yield_claims` now collects each item whose
claim here a yield of this branch's ended, and when it has nothing new to
write it asks `_on_remote` and finds that yield's commit with `_recorded`
(given `trailer="Yield"`). Where the remote's tip does not carry it, the run
goes to `_publish` as `claim`'s retry does: pushed where the remote has no
copy of the branch, or left local with `LOCAL_ONLY` and the push command named
where it has one. Two real-git tests in `subprojects/docket/tests/test_claiming.py`
hold the rerun, and both failed before the change.
