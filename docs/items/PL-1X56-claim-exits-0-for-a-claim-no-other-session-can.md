---
id: PL-1X56
title: claim exits 0 for a claim no other session can see, printing 'not pushed', while a failed push leaving the same invisible state exits 4, and every claim made after a branch's first push takes that path
priority: P2
effort: S
status: done
classes: defect
feature: claim-integrity
milestone: v0.5.12
touches: subprojects/docket/src/docket/claiming.py, subprojects/docket/src/docket/cli.py, subprojects/docket/tests/test_claiming.py, .claude/skills/docket/modes/start.md
deferred-from: v0.6.0 - filed 2026-09-25 by PL-P0FP's stress test, after the freeze, and not safety or science; a defect in the claim writer, which merged after the freeze
added: 2026-09-25
closed: 2026-09-25
pr: 1026
payoff: a session reads from claim's exit status alone whether every other session can see its claim, so a claim that still owes a push is never reported as held
verify: grep -q 'def test_a_claim_left_unpushed_on_a_branch_the_remote_has_exits_4' subprojects/docket/tests/test_claiming.py
recurrences: 2026-09-25 PL-NNLM
---

**Problem.** claim exits 0 for a claim no other session can see, printing 'not pushed', while a failed push leaving the same invisible state exits 4, and every claim made after a branch's first push takes that path

Reproduced (scenario i, and 9 distinct instances across 6 seeded random runs): `claim X` exits 0 with "not pushed"; a second clone fetches, `next` offers X, `show X` has no mark. It is the entry route to the late-claim displacement above. Related to PL-WX87, which covers only the stale-tracking-ref variant.

**Why it matters.** Exit status is what a session reports as evidence; 0 says the claim is visible when it is not.

**Done when.** An unpushed claim exits non-zero, or claim pushes; a test holds scenario i.

**Reproduced here, 2026-09-25**, on `claude/pl-1x56-g6jo7a`, pushed with nothing on
it: `bin/docket claim PL-1X56` wrote `e81a1bf4656f`, printed "not pushed: the
branch is on the remote as origin/claude/pl-1x56-g6jo7a", and exited 0; the
claim reached the remote only by the `git push` typed next. `claiming._publish`
declines to push where the branch has an upstream of its own or a copy on the
remote, then falls through to the read-back a pushed claim gets, and that
read-back answers from the clone's own refs, where the claim is live - so
`CLAIMED` (0) is what a claim nobody else can fetch exits with. `yield` goes
through the same function, and a yield no other session can see exits 0 the
same way while every other session goes on reading this branch as the holder.

**Decision (session, 2026-09-25): exit 4, and keep the refusal to push.** The
done-when admits either. Pushing was not taken because `claim` cannot tell an
armed pull request from an unarmed one - it knows nothing about the forge - and
a push onto an armed one merges the claim away with the branch, which is what
the refusal exists for (`PL-QP9Z`, ratified, and left standing). Exiting 4
states the fact the exit status is read for: `LOCAL_ONLY` already means "the
claim exists only in this checkout", and a claim left unpushed is in that
state whether a push failed or none was tried; the message still names the
push command and the disarm that comes first. `yield` takes the same code on
the same path, for the same reason. Pushing where the forge reports no pull
request open on the branch would spare the by-hand push a rider claim owes and
is `PL-62V1`, filed rather than built: it adds a forge read to `claim` under the
generator pause, and `PL-ZLJ9` is where the publish path is next reshaped.

**Generator check.** The fact misread is whether a claim written in this
checkout has reached the remote: `_publish`'s exit statuses were written for
two outcomes, pushed and push failed, and the third - deliberately not pushed -
fell through to the first's code. No head's `misread:` states it. `PL-4Q9B`'s is
the reverse direction, the clone's copies of the remote's refs going stale,
which is `PL-WX87`'s variant; `PL-MB2W`'s is who holds an item, which this
record answers correctly once it is fetched. One item misreads the fact, so a
one-off in the claim writer; the nine instances the stress test counted are
one defect met on every rider claim.

Evidence: `docs/stress-2026-09-25/evidence.tar.gz` (PL-P0FP).
