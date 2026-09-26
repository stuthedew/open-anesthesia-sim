---
id: PL-ZLJ9
title: A claim published late displaces one already confirmed first, because claims are ordered by commit author date rather than by when they became visible, and claim's retry path never asks whether a visible rival claimed in between
priority: P2
effort: S
status: done
classes: defect
feature: claim-integrity
touches: subprojects/docket/src/docket/claiming.py, subprojects/docket/src/docket/claims.py, subprojects/docket/src/docket/cli.py, subprojects/docket/tests/test_claiming.py, subprojects/docket/README.md, .claude/skills/docket/modes/start.md
deferred-from: v0.6.0 - filed 2026-09-25 by PL-P0FP's stress test, after the freeze, and not safety or science; a defect in the claim record's ordering, which merged after the freeze
added: 2026-09-25
closed: 2026-09-25
pr: 1028
payoff: a session told by claim's exit 0 that it holds an item keeps it: a claim written earlier but published later through claim yields instead of displacing it
verify: grep -q 'def test_a_claim_confirmed_first_is_not_displaced_by_one_published_later_through_push' subprojects/docket/tests/test_claiming.py && grep -q 'def test_a_retry_withdraws_a_claim_a_rival_published_over_while_it_was_unpublished' subprojects/docket/tests/test_claiming.py
---

**Problem.** A claim published late displaces one already confirmed first, because claims are ordered by commit author date rather than by when they became visible, and claim's retry path never asks whether a visible rival claimed in between

Reproduced (scenarios i2, a3): s1 captures and pushes, then `claim X` exits 0 with "not pushed"; s2 `claim X` exits 0, pushed, reads back first; s1 `git push`; now every fetched clone says s1 holds X and s2 is told "This branch yields: stop". Same via a failed push (exit 4) then a retry that exits 0 "already holds it first". Order `(%aI, hash)` is PL-MB2W's design; PL-J9S0's CI fence fires only after the fact.

**Why it matters.** Two sessions each told, in turn, that they hold the item: the duplicated-work failure the claim record exists to prevent.

**Done when.** `claim` publishes every claim itself, and an unpublished claim yields to any live rival already on the remote, so a claim confirmed first is never revoked by one published later through `claim`. A test holds scenario i2 with the late session publishing through `claim --push`, and a second holds scenario a3's retry. The residual, a stale claim published by a hand or work push, is recorded here rather than tested.

Evidence: `docs/stress-2026-09-25/evidence.tar.gz` (PL-P0FP).

**Reproduced again 2026-09-25 on `688827c1`**, after `PL-KX73` (#1020) and `PL-1X56` (#1026) merged, in a scratch test against a bare remote using `test_claiming.py`'s fixtures. Scenario i2: the first session's claim now exits 4, "not pushed", as `PL-1X56` intended. The second session claims five minutes later, pushes, and exits 0. The first then pushes by hand, and both a fresh clone and the second session read the first as holder. Scenario a3: a claim whose push failed is retried after a rival claimed, pushed and exited 0. The retry prints "already holds it first", pushes the older claim and exits 0, and a fresh clone reads the retried branch as holder. In both, the displaced session had been told by exit 0 that it held the item.

**Generator check.** The fact misread is `PL-MB2W`'s: who holds an item now. `PL-MB2W` recorded *that* a session holds an item, but left *which claim came first* to the author date, which is set when a claim is written rather than when other sessions can see it. So this is the head's own mechanism, a derived answer where a recorded one was wanted, reappearing at the ordering step. It was filed while the head is open, and the head's close-out waits on this item, so membership in its `root-cause-of:` is left to that close-out.

**This reopens a limitation the design accepted.** `.claude/skills/docket/modes/start.md` says `claim`'s read after its push "narrows the race rather than closing it: a claim written first and pushed last still orders first". `PL-MB2W`'s design round chose `(%aI, hash)` so that every checkout computes one order from one set of commits. The stress test (`PL-P0FP`) is the measurement that makes it reopenable.

**Why no change to the reader can close it.** Three facts combine:

- Every checkout must compute the order from the commits alone, and git records no push time. Author and committer dates are set when a commit is made.
- `claim` never pushes onto a branch the remote already has (`PL-QP9Z`), because an armed pull request would merge the claim away. The protocol this project's threads are briefed with, push the branch and then claim, takes that route every time, so a claim is written first and published later by a hand push.
- A hand push leaves no trace of when it happened. A third clone reading scenario i2 sees two claims dated 13:02 and 13:07 and nothing else, so it cannot tell that the 13:02 one was invisible when the 13:07 one was confirmed.

**Decision needed: how much of the accepted limitation to close.**

- **A. `claim` owns every publication, and an unpublished claim yields to every live rival already on the remote.** A retry, and the new `--push` below, first compare the claim with the remote. Where the claim is unpublished and a live rival is already on the remote, the claim is withdrawn, whatever its date: `claim` writes a `Yield:`, pushes it, and exits 3 with the yield line. [superseded 2026-09-25: the yield is committed and not pushed, as the build plan below says, since it matters only once the stale claim is published and rides that same push.] The route that now says "push it with `git push`" instead offers `--push`, by which the session says it has disarmed auto-merge. `claim` then pushes and reads back as it does on a new branch. The project's protocol would change to claim before the first push, since `PL-KX73` now lets `claim` push the web harness's own branch shape itself. This closes a3, and closes i2 wherever the late session publishes through `claim`. One residual stays, and no read can detect it: a session that ignores the message and publishes a stale claim with a hand or work push still displaces. Size S: `claiming.py`, `cli.py`, their tests, `start.md` and the exit-4 message. No reader changes.
- **B. A fence on the remote.** `claim` pushes the claim commit to a per-item ref, `refs/claims/<ID>`, with a compare-and-swap. The remote updates one ref atomically, so whoever creates it first holds the item, and no later push to a branch can move it. This closes i2 and a3 completely, the hand push included. Costs: new shared state on the remote with its own lifecycle (create on claim, delete on yield or close, compare-and-swap on takeover); every reader's ordering source changes; CI's checkout must fetch the namespace, since it fetches heads and tags today (`PL-J9S0`'s premise check); and it partly reverses the design's rule that a claim lives only on its holder's own branch. Unverified: whether GitHub and this environment's git proxy accept a push to a ref that is not a branch. Testing that writes to the repository outside a session branch, which needs the owner's word. Size L. It is not the dead end of an index committed beside the items: the ref cannot be recomputed from anything else, and refs are never merged.

**Recommended: A.** It closes both scenarios wherever sessions do what `claim` tells them. What it leaves is the class of race the design already accepts, and `show` still gives every clone the same verdict on who yields, so the cost of the residual is a handover rather than two sessions both continuing. B is close to a one-way door. It builds shared remote state on a platform capability nobody has checked, to remove a residual that needs a session to ignore `claim`'s own message. Take B only if "never revoked" must hold whatever a session does, and then its first step is a push to a scratch ref, made only on the owner's say-so. Under A, the Done-when's "a test holds scenario i2" would read: a test holds i2 with the late session publishing through `claim --push`, a second holds a3's retry, and the hand-push residual is recorded here rather than tested.

**Answered 2026-09-25 on the decision card in this item's project thread** (project owner, 2026-09-25, ratified, over the remote fence): route A, the claim-side fix. Before this answer the Done-when read: "A claim confirmed first-visible is never revoked by one published later; a test holds scenario i2." It now reads as the recommendation above said it would.

**Build plan, recorded 2026-09-25 before a context reset.**

- In `claiming.claim`'s per-key loop, where this branch's live hold orders first: if that hold's claim commit is not on `origin/<branch>` (`_published`), and a live rival on another branch has its claim commit on that branch's own remote copy, this branch does not hold the item. Write a `Yield:` for it on this branch, committed and not pushed, since it matters only once the stale claim is published and it rides that same push. Refuse the whole call, write no new claim, and exit 3 with a line naming the rival and the withdrawal commit. A rival that orders first by date is already refused by the existing rule, and a rival only in this checkout is not published, so neither is touched.
- `claim --push`: on a branch the remote already has, push and read back as on a new branch. `claim`'s exit-4 "not pushed" message names `bin/docket claim <IDs> --push`, after disarming auto-merge, instead of `git push`. A failed push's message says to run `claim` again rather than push by hand. `yield`'s messages keep `git push`, because a yield published late displaces nobody.
- Tests: the two `verify:` names, i2 with the late session publishing through `claim --push` and a3's retry, plus a `--push` happy path. Update the tests that assert `claim`'s old `git push --set-upstream` wording.
- Docs: `start.md`'s claim paragraphs, since exit 4 now names `--push` and the race paragraph gains the new rule and the residual; `subprojects/docket/README.md`'s `claim` lines; `claiming.py`'s docstring.
- Outside the repository: the project's claim protocol changes to claim before the first push, which is the owner's line to edit.

**Built 2026-09-25.** As planned, with one widening. The check runs over every live claim of the branch's, not only the ids asked for, because a push publishes all of them: after `claim A` was left unpushed, `claim B --push` would otherwise have published A unchecked. An id asked for that is withdrawn refuses the whole call with exit 3; one not asked for is withdrawn, reported, and the call goes on to what was asked. `claiming._displaced` finds them and `_withdraw` writes the yield. The rival test reads the clone's tracking ref for the rival's branch, fresh from `claim`'s own fetch; a deleted branch's stale ref errs toward yielding, as the existing first-by-date refusal already does. `claims.py`, the reader, is unchanged.

Tests: the two `verify:` names, and `test_a_claim_on_another_item_withdraws_a_displaced_claim_its_push_would_publish` for the widening. All three fail on the code before this item. The `--push` happy path ends `test_a_claim_left_unpushed_on_a_branch_the_remote_has_exits_4_because_no_other_session_sees_it`, and `test_a_branch_tracking_the_default_branch_already_on_the_remote_is_given_its_push_command` shows `--push` giving a branch that tracks `main` its own upstream without touching `main`.

Residuals, as the Done-when records: a stale claim published by a hand or work push skips the check, and two claims pushed in the same minute still order by date. `PL-WX87` (#1024) makes `_published` ask the remote with `git ls-remote` rather than read the tracking ref. Whichever of the two lands second makes `_displaced` use that answer for this branch's own claim.
