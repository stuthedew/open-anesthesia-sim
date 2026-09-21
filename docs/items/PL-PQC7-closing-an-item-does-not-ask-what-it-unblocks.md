---
id: PL-PQC7
title: Closing an item does not ask what it unblocks, so every promotable item waits for someone to run a deliberate grooming pass
priority: P2
effort: S
status: done
classes: defect
feature: stale-blocked-routing
milestone: v0.5.0
touches: subprojects/docket/src/docket/cli.py, subprojects/docket/tests/test_cli.py, subprojects/docket/README.md, .claude/skills/docket/SKILL.md, docs/items
added: 2026-09-20
closed: 2026-09-20
pr: 779
payoff: a blocker closing says what it just unblocked, instead of the reading waiting for somebody to notice and run a grooming pass - two sessions ran two over the same four items on one day
verify: grep -q 'def test_closing_an_item_names_what_it_just_unblocked' subprojects/docket/tests/test_cli.py
---

**Problem.** Closing an item does not ask what it unblocks, so every promotable item waits for someone to run a deliberate grooming pass

**Found by `PL-8G48`, 2026-09-20**, which was the second grooming pass in four
days over the same advisory, and which merged with `PL-CHQY` - a second session's
item for the identical batch, filed the same day.

**The mechanism.** `bin/docket check` prints "every blocker has closed; it is
ready to promote" whenever a blocker closes. Nothing routes that line to
anybody: it is a standing advisory that only a session running a deliberate
grooming pass ever acts on, and such a pass has to be noticed, filed and
triaged before it can be run. In the meantime `bin/docket next` reads `status`
literally, so the items sit unofferable.

**The recommendation this records** was made in `PL-CHQY`'s own brief and put to
the project owner in the reply that filed it; `PL-CHQY` has since closed, so
without this item the recommendation exists nowhere in the tree. It is: make
*"what does this close unblock?"* part of the `docket` skill's close-out, where
the session closing an item is the one that already knows what its closure
means, rather than leaving the question to a later session reading a store it
has no context for.

**Why that placement rather than a check.** The decidable half - which items name
this one in `blocked-by`, and whether all their blockers are now closed - is
already computed and already printed. What is missing is judgment, and this pass
measured how much: of four items the advisory named, one was promotable, one had
already been done inside its own blocker, one had a user-facing question written
into it, and one was held by two conditions nobody had written down. The session
that closes the blocker is the cheapest place to get that judgment, because it
is holding the context the judgment needs.

**Related, and not a duplicate.** `PL-6T44` (docket next and wave read `status:
blocked` literally) is the *ranking* half of the same problem and is a recorded
generator at `needs-decision`; its three options all change what the commands
print. This is the *routing* half: a fourth route that changes when the question
is asked rather than how the answer is displayed. Whoever answers `PL-6T44`
should read this item first - it may be that one fix makes the other
unnecessary, and deciding that is part of `PL-6T44`'s decision rather than this
item's.

**Why it matters.** `bin/docket next` reads `status` literally, so a blocked
item whose blockers have all closed is startable work nobody is offered - and
where the item is `safety` or `science` and also `anticipated`, the stale
`blocked` is what holds the finding outside the debt gate built to catch it,
since `check_gate_reentries` exempts it only while the two hold together
(`PL-ZF2G`). The cost is paid again on every closure that releases something:
`PL-1FT6` alone holds 8 items directly, with `PL-W9P6` another 6 behind it.

**Done when.** Closing an item names the items that closure takes the last
recorded blocker off, at the moment of the closure rather than in a later
grooming pass, and the `docket` skill's close-out says to act on them there; a
test under `subprojects/docket/tests/` drives a closure that releases one item
and a closure that releases none.

## Decision, 2026-09-20: derive it at close time; no `blocking:` field

**The project owner asked whether a `blocking:` field had been implemented** -
the other side of `blocked-by`, so that closing an item would say what to go
and unblock. It never was, and the answer taken is the close-time print
instead (project owner, 2026-09-20, ratified, over adding the stored field).

**What made the field look like the answer.** `Item.blocking_items` in
`subprojects/docket/src/docket/model.py` reads like the reverse edge and is the
forward one: it is the `blocked-by` entries naming a queue item, with the
milestone entries stripped. Every reader meeting that name cold has reason to
believe the reverse edge is already stored.

**Why the field was refused.** It denormalizes an edge the store already
derives, so it adds a second place the relation can be written wrong and a
`docket check` rule to keep the two in agreement - and this store's own dead
ends already refuse a committed index on that reasoning
(`subprojects/docket/src/docket/store.py`). It also buys nothing at the moment
of closure: with `blocking:` on the closing item, the blocked item's status is
still a hand edit. It says where to look; it does not look. And it inherits the
same blind spot the derived reading has - `PL-JFQ3` found 3 of 9 and `PL-8G48`
2 of 4 held by a condition nobody had written into any field, which no reverse
edge reaches.

**What was built instead.** `bin/docket set <id> --status done|dropped` now
names the items that closure takes the last recorded blocker off, and the
`docket` skill's close-out step 1 says to act on them there rather than
deferring to a pass. The decidable half - which items name this one, and
whether their every blocker is now closed - was already `plan.promotable`; the
judgment half stays with the session closing the blocker, which is the cheapest
place to get it because it is already holding the context.

**Newly promotable, not the standing set.** `cli._say_promotable` prints the
whole stale-blocked backlog to a session choosing work. This prints only what
the write released, which is the half no other command can attribute to a
cause, and keeps the standing backlog off the one reader who did not cause it.

**Where the fan-out is, measured 2026-09-20** across the 39 open `blocked`
items: `PL-1FT6` (build the `LayoutModel`) holds 8 directly and `PL-W9P6`
another 6 behind it, so the print pays most on exactly the closure where a
session would otherwise have the most to reconstruct.
