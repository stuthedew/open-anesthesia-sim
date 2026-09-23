---
id: PL-MB2W
title: Whether a branch holds a claim is read from where its commits wrote and which id leads their subjects, never from what the branch does to the item, so docket flight and the auto-merge arming rule each misread every new shape of queue-only work until it gets its own exception
priority: P2
effort: M
status: needs-decision
classes: defect
feature: parallel-sessions
touches: subprojects/docket/src/docket/vcs.py, subprojects/docket/tests/test_vcs.py, subprojects/docket/README.md, .claude/skills/docket/modes/start.md, CLAUDE.md
added: 2026-09-23
payoff: a claim is read one way, by code, for flight, show, next and the auto-merge arming rule alike, so a new shape of queue-only work stops costing an item per reader
root-cause-of: PL-X3WZ, PL-7790, PL-N1JK, PL-VYSP, PL-3W3P, PL-8FJK, PL-8GV1, PL-QP9Z, PL-1MCK, PL-KWCY, PL-VFJ3
generator: live - whether a branch holds a claim is read from where its commits wrote and which id leads their subjects, never from what the branch does to the item, so each new shape of queue-only work is misread until it gets its own exception; four members were filed after PL-8FJK's fix merged on 2026-09-22 (PL-QP9Z, PL-1MCK, PL-KWCY, PL-VFJ3) and PL-8GV1 with it
---

**Problem.** A claim, meaning a session working an item on a branch, has no
record of its own. Every reader rebuilds it from the shape of the branch's
commits: where each commit wrote, and which id leads its subject. There are
two readers, and each one has been patched one shape at a time.

- **`docket flight`, `show` and `next`** read `vcs._annotates_only`. It counts
  a queue-only commit as a note, never as work, and `vcs._own_edit_claims`
  promotes three shapes back to claims: an item whose deliverable is the queue
  (`PL-7790`), a design round at `needs-decision` (`PL-VYSP`), and a branch
  closing an item the base holds open (`PL-8FJK`). Each promotion followed an
  incident. `PL-X3WZ` was a note read as work. `PL-N1JK` was a triage pass that
  could raise no mark. `PL-3W3P` was a pass claiming items for another id's
  reason. `PL-8GV1`, a pass blocking an item it never claimed, would need a
  fourth promotion. It was dropped on its count, and the drop did not change
  its mechanism. The inverse error is also live: a non-queue commit led by an
  id claims that item. `#953`'s fix commit, led by three triaged ids, showed
  `PL-JD4L` in flight with no work on it (`PL-VFJ3`, second half).
- **The auto-merge arming rule in `CLAUDE.md`** decides that a branch is safe
  to merge because only item files ride it, which is the same where-it-wrote
  test. It then has to exempt claims, and it took three patches in one day to
  find which claims those are: `PL-QP9Z` (the empty start claim), `PL-1MCK`
  (queue-only claims, and claims made on an earlier push), and `PL-KWCY` (a
  claim whose item is closed). The rule now defers to "a queue-only commit
  that start mode reads as one". That ties it to the catalog `vcs.py`
  implements, but it keeps that catalog as prose, applied by each session's
  judgment.

**Generator check.** This is the head. It was verified on 2026-09-23 against
the two closed `live` verdicts it named, under `PL-TH9K`.

- It is `PL-8FJK`'s mechanism, one level up. That head's fix (`#926`) gave
  the three promotions one feed and one helper. Its own verdict records that
  this did not stop the per-shape half, and four instances have been filed
  since the fix merged (`PL-QP9Z`, `PL-1MCK`, `PL-KWCY`, `PL-VFJ3`), with
  `PL-8GV1` filed in the same pull request. `PL-8FJK`'s verdict now points
  here.
- It is not `PL-WNCT`'s mechanism. `PL-WNCT` is about captures stranded on
  branches that have no pull request. The three arming patches are side
  effects of `PL-WNCT`'s fix, because that fix introduced the arming rule.
  They are not stranding.
- `verify`'s batch note (`PL-4LT9`) is left out. It asks which commits are an
  item's work, for a scope audit, rather than whether anyone holds the item.
  It is also reported rather than repaired by design, and nothing has been
  filed against it since.
- `PL-KWCY`'s own check found no generator, and that was right at its
  altitude, where the arming rule alone has two members. It does not survive
  at this altitude, where the arming rule and `flight` share one design fact.

**Why it matters.** It ranks as a generator because it keeps producing
members. Every new kind of queue-only pass adds a shape, and each misread shape
costs a collision or a false mark in `flight`, or a lost claim at merge. Each
shape has cost a separate item. The arming half is also judgment a session
applies from prose, although the answer is decidable from the branch. That is
the reverse of `CLAUDE.md` § "Prefer deterministic tooling over repeated model
work".

**Decision needed.** What `flight` and the arming rule should read a claim
from. The decision belongs to a session, not the owner: it changes internal
structure, and no learner would see the result.

1. **What the branch does to the item.** Replace the per-shape promotions with
   one comparison of the item's front matter at the tip against the base, for
   status and `blocked-by`. Add the empty `<id>: start` commit that start mode
   already requires. A queue-only branch then claims an item when it moves the
   item's state or carries the start commit. This covers the closure and block
   shapes without enumerating them. Its cost: a design round that writes only
   prose and never pushed its start commit reads as a note.
2. **Keep the per-shape promotions** and add `PL-8GV1`'s block shape as the
   fourth. This is the cheapest option, and it is the accretion this verdict
   names.
3. **Explicit claims only.** Only the start commit, and work outside the queue,
   claims an item, and every promotion is deleted. This gives the simplest
   reader. It moves the failure onto any session that skips the start commit,
   which is exactly the failure the promotions were built to catch.

**Recommended: route 1, and move the arming rule's claim test into code.**
Implement one predicate in `vcs.py` that `flight`, `show` and `next` read.
Replace the arming rule's prose with "arm only where `bin/docket flight` names
no claim on an open item on this branch". The arming half then reads the
catalog the code keeps instead of a restatement of it. `PL-VFJ3`'s false claim
is a different direction, and route 1 does not fix it. The fix there is to lead
a pass's commits with the pass's own id, which is `CLAUDE.md` § "Housekeeping
you are about to do yourself is filed before you do it".

**Done when.** The following holds on route 1, and the design round rewrites
this section if it picks another route.

- One predicate decides a claim for `flight`, `show`, `next` and the arming
  decision.
- A queue-only pass that closes or blocks an item it never claimed reads as
  in flight, with no promotion specific to that shape.
- `CLAUDE.md`'s arming rule names that predicate's command instead of
  restating start mode's catalog.
